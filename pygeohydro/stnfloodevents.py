"""Access USGS Short-Term Network (STN) via Restful API."""

from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING, Any, Union

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import CRS

import async_retriever as ar
from pygeohydro.exceptions import InputValueError
from pygeoogc import ServiceURL

if TYPE_CHECKING:
    CRSTYPE = Union[int, str, CRS]

__all__ = ["STNFloodEventData", "stn_flood_event"]


class STNFloodEventData:
    """Client for STN Flood Event Data's RESTFUL Service API.

    Advantages of using this client are:
    - The user does not need to know the details of RESTFUL in
      general and of this API specifically.
    - Parses the data and returns Python objects
      (e.g., pandas.DataFrame, geopandas.GeoDataFrame) instead of JSON.
    - Convenience functions are offered for data dictionaries.
    - Geo-references the data where applicable.

    Attributes
    ----------
    service_url : str
        The service url of the STN Flood Event Data RESTFUL Service API.
    data_dictionary_url : str
        The data dictionary url of the STN Flood Event Data RESTFUL Service API.
    service_crs : int, str, or CRS, optional
        The coordinate reference system of the data from the service, defaults
        to ``EPSG:4326``.
    instruments_query_params : set of str
        The accepted query parameters for the instruments data type.
    peaks_query_params : set of str
        The accepted query parameters for the peaks data type.
    hwms_query_params : set of str
        The accepted query parameters for the hwms data type.
    sites_query_params : set of str
        The accepted query parameters for the sites data type.

    Methods
    -------
    data_dictionary
        Retrieves the data dictionary for a given data type.
    get_all_data
        Retrieves all data for a given data type.
    get_filtered_data
        Retrieves filtered data for a given data type.

    Notes
    -----
    Point data from the service is assumed to be in the WGS84
    coordinate reference system (EPSG:4326).

    References
    ----------
    * `USGS Short-Term Network (STN) <https://stn.wim.usgs.gov/STNWeb/#/>`_
    * `All Sensors API Documentation <https://stn.wim.usgs.gov/STNServices/Documentation/Sensor/AllSensors>`_
    * `All Peak Summary API Documentation <https://stn.wim.usgs.gov/STNServices/Documentation/PeakSummary/AllPeakSummaries>`_
    * `All HWM API Documentation <https://stn.wim.usgs.gov/STNServices/Documentation/HWM/AllHWMs>`_
    * `All Sites API Documentation <https://stn.wim.usgs.gov/STNServices/Documentation/Site/AllSites>`_
    * `USGS Flood Event Viewer: Providing Hurricane and Flood Response Data <https://www.usgs.gov/mission-areas/water-resources/science/usgs-flood-event-viewer-providing-hurricane-and-flood>`_
    * `A USGS guide for finding and interpreting high-water marks <https://www.usgs.gov/media/videos/a-usgs-guide-finding-and-interpreting-high-water-marks>`_
    * `High-Water Marks and Flooding <https://www.usgs.gov/special-topics/water-science-school/science/high-water-marks-and-flooding>`_
    * `Identifying and preserving high-water mark data <https://doi.org/10.3133/tm3A24>`_
    """

    # Per Athena Clark, Lauren Privette, and Hans Vargas at USGS
    # this is the CRS used for visualization on STN front-end.
    service_crs: int = 4326
    service_url: str = ServiceURL().restful.stnflood
    data_dictionary_url: str = ServiceURL().restful.stnflood_dd
    instruments_query_params: set[str] = {
        "Event",
        "EventType",
        "EventStatus",
        "States",
        "County",
        "CurrentStatus",
        "CollectionCondition",
        "SensorType",
        "DeploymentType",
    }
    peaks_query_params: set[str] = {
        "Event",
        "EventType",
        "EventStatus",
        "States",
        "County",
        "StartDate",
        "EndDate",
    }
    hwms_query_params: set[str] = {
        "Event",
        "EventType",
        "EventStatus",
        "States",
        "County",
        "StartDate",
        "EndDate",
    }
    sites_query_params: set[str] = {
        "Event",
        "State",
        "SensorType",
        "NetworkName",
        "OPDefined",
        "HWMOnly",
        "HWMSurveyed",
        "SensorOnly",
        "RDGOnly",
        "HousingTypeOne",
        "HousingTypeSeven",
    }

    @classmethod
    def _geopandify(
        cls,
        input_list: list[dict[str, Any]],
        x_col: str,
        y_col: str,
        crs: CRSTYPE,
    ) -> gpd.GeoDataFrame:
        """Georeference a list of dictionaries to a GeoDataFrame.

        Parameters
        ----------
        input_list : list of dict
            The list of dictionaries to be converted to a geodataframe.
        x_col : str
            The name of the column containing the x-coordinate.
        y_col : str
            The name of the column containing the y-coordinate.
        crs : int, str, or CRS
            Desired Coordinate reference system (CRS) of output.
            Only used for GeoDataFrames outputs.

        Returns
        -------
        geopandas.GeoDataFrame
            The geo-referenced GeoDataFrame.
        """
        df = pd.DataFrame(input_list)

        if crs is None:
            crs = cls.service_crs

        return gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df[x_col], df[y_col], crs=cls.service_crs),
        ).to_crs(crs)

    @classmethod
    def _delist_dict(cls, d: dict[str, list[float] | float]) -> dict[str, float]:
        """De-lists all unit length lists in a dictionary."""

        def delist(x: list[float] | float) -> float:
            if isinstance(x, list) and len(x) == 1:
                return x[0]
            if isinstance(x, list) and len(x) == 0:
                return np.nan
            return x

        return {k: delist(v) for k, v in d.items()}

    @classmethod
    def data_dictionary(
        cls, data_type: str, as_dict: bool = False, async_retriever_kwargs: dict | None = None
    ) -> pd.DataFrame | dict[str, Any]:
        """Retrieve data dictionaries from the STN Flood Event Data API.

        Parameters
        ----------
        data_type : str
            The data source from STN Flood Event Data API.
            It can be ``instruments``, ``peaks``, ``hwms``, or ``sites``.
        as_dict : bool, default = False
            If True, return the data dictionary as a dictionary.
            Otherwise, it returns as ``pandas.DataFrame``.
        async_retriever_kwargs : dict, optional
            Additional keyword arguments to pass to
            ``async_retriever.retrieve_json()``. The ``url`` and ``request_kwds``
            options are already set.

        Returns
        -------
        pandas.DataFrame or dict
            The retrieved data dictionary as pandas.DataFrame or dict.

        See Also
        --------
        :meth:`~get_all_data` : Retrieves all data for a given data type.
        :meth:`~get_filtered_data` : Retrieves filtered data for a given data type.

        Examples
        --------
        >>> from pygeohydro.stnfloodevents import STNFloodEventData
        >>> data = STNFloodEventData.data_dictionary(data_type="instruments", as_dict=False)
        >>> data.shape[1]
        2
        >>> data.columns
        Index(['Field', 'Definition'], dtype='object')
        """
        dtype_dict = {
            "instruments": "Instruments.csv",
            "peaks": "FilteredPeaks.csv",
            "hwms": "FilteredHWMs.csv",
            "sites": "sites.csv",
        }

        try:
            endpoint = dtype_dict[data_type]
        except KeyError as ke:
            raise InputValueError(data_type, list(dtype_dict.keys())) from ke

        if async_retriever_kwargs is None:
            async_retriever_kwargs = {}
        else:
            async_retriever_kwargs.pop("url", None)

        resp = ar.retrieve_text([f"{cls.data_dictionary_url}{endpoint}"], **async_retriever_kwargs)
        data = pd.read_csv(StringIO(resp[0]))

        if "Field" not in data.columns:
            data.iloc[0] = data.columns.tolist()
            data.columns = ["Field", "Definition"]

        data["Definition"] = data["Definition"].str.replace("\r\n", "  ")

        # concatenate definitions corresponding to NaN fields until
        # a non-NaN field is encountered
        data_dict = {"Field": [], "Definition": []}

        for _, row in data.iterrows():
            if pd.isna(row["Field"]):
                data_dict["Definition"][-1] += " " + row["Definition"]
            else:
                data_dict["Field"].append(row["Field"])
                data_dict["Definition"].append(row["Definition"])

        if as_dict:
            return data_dict
        return pd.DataFrame(data_dict)

    @classmethod
    def get_all_data(
        cls,
        data_type: str,
        as_list: bool = False,
        crs: str | None = service_crs,
        async_retriever_kwargs: dict | None = None,
    ) -> gpd.GeoDataFrame | pd.DataFrame | list[dict[str, Any]]:
        """Retrieve all data from the STN Flood Event Data API.

        Parameters
        ----------
        data_type : str
            The data source from STN Flood Event Data API.
            It can be ``instruments``, ``peaks``, ``hwms``, or ``sites``.
        as_list : bool, optional
            If True, return the data as a list, defaults to False.
        crs : int, str, or CRS, optional
            Desired Coordinate reference system (CRS) of output.
            Only used for GeoDataFrames with ``hwms`` and ``sites`` data types.
        async_retriever_kwargs : dict, optional
            Additional keyword arguments to pass to
            ``async_retriever.retrieve_json()``. The ``url`` and ``request_kwds``
            options are already set.

        Returns
        -------
        geopandas.GeoDataFrame or pandas.DataFrame or list of dict
            The retrieved data as a GeoDataFrame, DataFrame, or a list of dictionaries.

        Raises
        ------
        InputValueError
            If the input data_type is not one of
            ``instruments``, ``peaks``, ``hwms``, or ``sites``

        See Also
        --------
        :meth:`~get_filtered_data` : Retrieves filtered data for a given data type.
        :meth:`~get_data_dictionary` : Retrieves the data dictionary for a given data type.

        Notes
        -----
        Notice schema differences between the data dictionaries, filtered data
        queries, and all data queries. This is a known issue and is being addressed
        by USGS.

        Examples
        --------
        >>> from pygeohydro.stnfloodevents import STNFloodEventData
        >>> data = STNFloodEventData.get_all_data(data_type="instruments")
        >>> data.shape[1]
        18
        >>> data.columns
        Index(['instrument_id', 'sensor_type_id', 'deployment_type_id',
               'location_description', 'serial_number', 'interval', 'site_id',
               'event_id', 'inst_collection_id', 'housing_type_id', 'sensor_brand_id',
               'vented', 'instrument_status', 'data_files', 'files', 'last_updated',
               'last_updated_by', 'housing_serial_number'],
               dtype='object')
        """
        endpoint_dict = {
            "instruments": "Instruments.json",
            "peaks": "PeakSummaries.json",
            "hwms": "HWMs.json",
            "sites": "Sites.json",
        }

        try:
            endpoint = endpoint_dict[data_type]
        except KeyError as ke:
            raise InputValueError(data_type, list(endpoint_dict.keys())) from ke

        if async_retriever_kwargs is None:
            async_retriever_kwargs = {}
        else:
            _ = async_retriever_kwargs.pop("url", None)

        resp = ar.retrieve_json([f"{cls.service_url}{endpoint}"], **async_retriever_kwargs)
        data = [cls._delist_dict(d) for d in resp[0]]

        if as_list:
            return data

        xy_cols = {
            "instruments": None,
            "peaks": None,
            "hwms": ("longitude_dd", "latitude_dd"),
            "sites": ("longitude_dd", "latitude_dd"),
        }
        if xy_cols[data_type] is None:
            return pd.DataFrame(data)

        x_col, y_col = xy_cols[data_type]
        return cls._geopandify(data, x_col, y_col, crs)

    @classmethod
    def get_filtered_data(
        cls,
        data_type: str,
        query_params: dict | None = None,
        as_list: bool | None = False,
        crs: str | None = service_crs,
        async_retriever_kwargs: dict | None = None,
    ) -> gpd.GeoDataFrame | pd.DataFrame | list[dict[str, Any]]:
        """Retrieve filtered data from the STN Flood Event Data API.

        Parameters
        ----------
        data_type : str
            The data source from STN Flood Event Data API.
            It can be ``instruments``, ``peaks``, ``hwms``, or ``sites``.
        query_params : dict, optional
            RESTFUL API query parameters. For accepted values, see
            the STNFloodEventData class attributes ``instruments_accepted_params``,
            ``peaks_accepted_params``, ``hwms_accepted_params``, and
            ``sites_accepted_params`` for available values.

            Also, see the API documentation for each data type for more information:
                - `instruments <https://stn.wim.usgs.gov/STNServices/Documentation/Sensor/FilteredSensors>`_
                - `peaks <https://stn.wim.usgs.gov/STNServices/Documentation/PeakSummary/FilteredPeakSummaries>`_
                - `hwms <https://stn.wim.usgs.gov/STNServices/Documentation/HWM/FilteredHWMs>`_
                - `sites <https://stn.wim.usgs.gov/STNServices/Documentation/Site/FilteredSites>`_

        as_list : bool, optional
            If True, return the data as a list, defaults to False.
        crs : int, str, or CRS, optional
            Desired Coordinate reference system (CRS) of output.
            Only used for GeoDataFrames outputs.
        async_retriever_kwargs : dict, optional
            Additional keyword arguments to pass to
            ``async_retriever.retrieve_json()``. The ``url`` and ``request_kwds``
            options are already set.

        Returns
        -------
        geopandas.GeoDataFrame or pandas.DataFrame or list of dict
            The retrieved data as a GeoDataFrame, DataFrame, or a
            list of dictionaries.

        Raises
        ------
        InputValueError
            If the input data_type is not one of
            ``instruments``, ``peaks``, ``hwms``, or ``sites``
        InputValueError
            If any of the input query_params are not in accepted
            parameters (See :meth:`~instruments_accepted_params`,
            :meth:`~peaks_accepted_params`, :meth:`~hwms_accepted_params`,
            or :meth:`~sites_accepted_params`).

        See Also
        --------
        :meth:`~get_all_data` : Retrieves all data for a given data type.
        :meth:`~get_data_dictionary` : Retrieves the data dictionary for a
        given data type.

        Notes
        -----
        Notice schema differences between the data dictionaries,
        filtered data queries, and all data queries. This is a known
        issue and is being addressed by USGS.

        Examples
        --------
        >>> from pygeohydro.stnfloodevents import STNFloodEventData
        >>> query_params = {"States": "SC, CA"}
        >>> data = STNFloodEventData.get_filtered_data(data_type="instruments", query_params=query_params)
        >>> data.shape[1]
        34
        >>> data.columns
        Index(['sensorType', 'deploymentType', 'eventName', 'collectionCondition',
            'housingType', 'sensorBrand', 'statusId', 'timeStamp', 'site_no',
            'latitude', 'longitude', 'siteDescription', 'networkNames', 'stateName',
            'countyName', 'siteWaterbody', 'siteHDatum', 'sitePriorityName',
            'siteZone', 'siteHCollectMethod', 'sitePermHousing', 'instrument_id',
            'sensor_type_id', 'deployment_type_id', 'location_description',
            'serial_number', 'housing_serial_number', 'interval', 'site_id',
            'vented', 'instrument_status', 'data_files', 'files', 'geometry'],
            dtype='object')
        """
        endpoint_dict = {
            "instruments": "Instruments/FilteredInstruments.json",
            "peaks": "PeakSummaries/FilteredPeaks.json",
            "hwms": "HWMs/FilteredHWMs.json",
            "sites": "Sites/FilteredSites.json",
        }

        try:
            endpoint = endpoint_dict[data_type]
        except KeyError as ke:
            raise InputValueError(data_type, list(endpoint_dict.keys())) from ke

        allowed_query_param_dict = {
            "instruments": cls.instruments_query_params,
            "peaks": cls.peaks_query_params,
            "hwms": cls.hwms_query_params,
            "sites": cls.sites_query_params,
        }

        allowed_query_params = allowed_query_param_dict[data_type]

        if query_params is None:
            query_params = {}

        if not set(query_params.keys()).issubset(allowed_query_params):
            raise InputValueError("query_param", allowed_query_params)

        if async_retriever_kwargs is None:
            async_retriever_kwargs = {}
        else:
            async_retriever_kwargs.pop("url", None)
            async_retriever_kwargs.pop("request_kwds", None)

        resp = ar.retrieve_json(
            [f"{cls.service_url}{endpoint}"],
            request_kwds=[{"params": query_params}],
            **async_retriever_kwargs,
        )
        data = [cls._delist_dict(d) for d in resp[0]]
        if as_list:
            return data

        xy_cols = {
            "instruments": ("longitude", "latitude"),
            "peaks": ("longitude_dd", "latitude_dd"),
            "hwms": ("longitude", "latitude"),
            "sites": ("longitude_dd", "latitude_dd"),
        }
        x_col, y_col = xy_cols[data_type]
        return cls._geopandify(data, x_col, y_col, crs)


def stn_flood_event(data_type: str, query_params: dict | None = None) -> gpd.GeoDataFrame | pd.DataFrame:
    """Retrieve data from the STN Flood Event Data API.

    Parameters
    ----------
    data_type : str
        The data source from STN Flood Event Data API.
        It can be ``instruments``, ``peaks``, ``hwms``, or ``sites``.
    query_params : dict, optional
        RESTFUL API query parameters, defaults to ``None`` which returns
        all the available data for the given ``data_type``.
        For accepted values, see the STNFloodEventData class attributes
        :class:`STNFloodEventData.instruments_accepted_params`,
        :class:`STNFloodEventData.peaks_accepted_params`,
        :class:`STNFloodEventData.hwms_accepted_params`, and
        :class:`STNFloodEventData.sites_accepted_params` for available values.

        Also, see the API documentation for each data type for more information:
        - `instruments <https://stn.wim.usgs.gov/STNServices/Documentation/Sensor/FilteredSensors>`_
        - `peaks <https://stn.wim.usgs.gov/STNServices/Documentation/PeakSummary/FilteredPeakSummaries>`_
        - `hwms <https://stn.wim.usgs.gov/STNServices/Documentation/HWM/FilteredHWMs>`_
        - `sites <https://stn.wim.usgs.gov/STNServices/Documentation/Site/FilteredSites>`_

    as_list : bool, optional
        If True, return the data as a list, defaults to False.

    Returns
    -------
    geopandas.GeoDataFrame or pandas.DataFrame or list of dict
        The retrieved data as a GeoDataFrame, DataFrame, or a
        list of dictionaries.

    Raises
    ------
    InputValueError
        If the input data_type is not one of
        ``instruments``, ``peaks``, ``hwms``, or ``sites``
    InputValueError
        If any of the input query_params are not in accepted
        parameters.

    References
    ----------
    * `USGS Short-Term Network (STN) <https://stn.wim.usgs.gov/STNWeb/#/>`_
    * `Filtered Sensors API Documentation <https://stn.wim.usgs.gov/STNServices/Documentation/Sensor/FilteredSensors>`_
    * `Peak Summary API Documentation <https://stn.wim.usgs.gov/STNServices/Documentation/PeakSummary/FilteredPeakSummaries>`_
    * `Filtered HWM API Documentation <https://stn.wim.usgs.gov/STNServices/Documentation/HWM/FilteredHWMs>`_
    * `Filtered Sites API Documentation <https://stn.wim.usgs.gov/STNServices/Documentation/Site/FilteredSites>`_
    * `USGS Flood Event Viewer: Providing Hurricane and Flood Response Data <https://www.usgs.gov/mission-areas/water-resources/science/usgs-flood-event-viewer-providing-hurricane-and-flood>`_
    * `A USGS guide for finding and interpreting high-water marks <https://www.usgs.gov/media/videos/a-usgs-guide-finding-and-interpreting-high-water-marks>`_
    * `High-Water Marks and Flooding  <https://www.usgs.gov/special-topics/water-science-school/science/high-water-marks-and-flooding>`_
    * `Identifying and preserving high-water mark data <https://doi.org/10.3133/tm3A24>`_

    Notes
    -----
    Notice schema differences between the data dictionaries,
    filtered data queries, and all data queries. This is a known
    issue and is being addressed by USGS.

    Examples
    --------
    >>> from pygeohydro.stnfloodevents import STNFloodEventData
    >>> query_params = {"States": "SC, CA"}
    >>> data = stn_flood_event("instruments", query_params=query_params)
    >>> data.shape[1]
    34
    >>> data.columns
    Index(['sensorType', 'deploymentType', 'eventName', 'collectionCondition',
        'housingType', 'sensorBrand', 'statusId', 'timeStamp', 'site_no',
        'latitude', 'longitude', 'siteDescription', 'networkNames', 'stateName',
        'countyName', 'siteWaterbody', 'siteHDatum', 'sitePriorityName',
        'siteZone', 'siteHCollectMethod', 'sitePermHousing', 'instrument_id',
        'sensor_type_id', 'deployment_type_id', 'location_description',
        'serial_number', 'housing_serial_number', 'interval', 'site_id',
        'vented', 'instrument_status', 'data_files', 'files', 'geometry'],
        dtype='object')
    """
    if query_params is None:
        return STNFloodEventData.get_all_data(data_type=data_type)
    return STNFloodEventData.get_filtered_data(data_type=data_type, query_params=query_params)
