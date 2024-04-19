from caproto.server import pvproperty, ioc_arg_parser, run
from plugin_base import PluginBase, pvproperty_rbv
from textwrap import dedent


class StatsPlugin(PluginBase):
    """
    A PV Group that generates the PVs associated with an Area Detector Stats Plugin.

    NOTES:
    1. Unless otherwise listed in the notes below the PVs generated are 'Dummy' PVs
    that are not modified by any inputs, or modify any other PVs, except there own
    values when they are updated.

    TODO:
    1. ...
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # call the PluginBase __init__ function

    bgd_width = pvproperty_rbv(name=':BgdWidth', dtype=float)

    centroid_threshold = pvproperty_rbv(name=':CentroidThreshold', dtype=float)
    centroid_x = pvproperty(name=':CentroidX_RBV', dtype=float, read_only=True)
    centroid_y = pvproperty(name=':CentroidY_RBV', dtype=float, read_only=True)
    compute_centroid = pvproperty_rbv(name=':ComputeCentroid', dtype=bool)
    compute_histogram = pvproperty_rbv(name=':ComputeHistogram', dtype=bool)
    compute_profiles = pvproperty_rbv(name=':ComputeProfiles', dtype=bool)
    compute_statistics = pvproperty_rbv(name=':ComputeStatistics', dtype=bool)

    cursor_x = pvproperty_rbv(name=':CursorX', dtype=float)
    cursor_y = pvproperty_rbv(name=':CursorY', dtype=float)

    hist_entropy = pvproperty(name=':HistEntropy_RBV', dtype=float, read_only=True)
    hist_max = pvproperty_rbv(name=':HistMax', dtype=float)
    hist_min = pvproperty_rbv(name=':HistMin', dtype=float)
    hist_size = pvproperty_rbv(name=':HistSize', dtype=int)
    histogram = pvproperty(name=':Histogram_RBV', dtype=float)

    max_size_x = pvproperty(name=':MaxSizeX', dtype=int)
    max_size_y = pvproperty(name=':MaxSizeY', dtype=int)
    max_value = pvproperty(name=':MaxValue_RBV', dtype=float, read_only=True)
    max_x = pvproperty(name=':MaxX_RBV', dtype=float, read_only=True)
    max_y = pvproperty(name=':MaxY_RBV', dtype=float, read_only=True)
    mean_value = pvproperty(name=':MeanValue_RBV', dtype=float, read_only=True)
    min_value = pvproperty(name=':MinValue_RBV', dtype=float, read_only=True)
    min_x = pvproperty(name=':MinX_RBV', dtype=float, read_only=True)
    min_y = pvproperty(name=':MinY_RBV', dtype=float, read_only=True)
    net = pvproperty(name=':Net_RBV', dtype=float, read_only=True)

    profile_average_x = pvproperty(name=':ProfileAverageX_RBV', dtype=float, read_only=True)
    profile_average_y = pvproperty(name=':ProfileAverageY_RBV', dtype=float, read_only=True)
    profile_centroid_x = pvproperty(name=':ProfileCentroidX_RBV', dtype=float, read_only=True)
    profile_centroid_y = pvproperty(name=':ProfileCentroidY_RBV', dtype=float, read_only=True)
    profile_cursor_x = pvproperty(name=':ProfileCursorX_RBV', dtype=float, read_only=True)
    profile_cursor_y = pvproperty(name=':ProfileCursorY_RBV', dtype=float, read_only=True)
    profile_size_x = pvproperty(name=':ProfileSizeX_RBV', dtype=float, read_only=True)
    profile_size_y = pvproperty(name=':ProfileSizeY_RBV', dtype=float, read_only=True)
    profile_threshold_x = pvproperty(name=':ProfileThresholdX_RBV', dtype=float, read_only=True)
    profile_threshold_y = pvproperty(name=':ProfileThresholdY_RBV', dtype=float, read_only=True)

    set_x_hopr = pvproperty(name=':SetXHOPR', dtype=float)
    set_y_hopr = pvproperty(name=':SetYHOPR', dtype=float)

    sigma_xy = pvproperty(name=':SigmaXY_RBV', dtype=float, read_only=True)
    sigma_x = pvproperty(name=':SigmaX_RBV', dtype=float, read_only=True)
    sigma_y = pvproperty(name=':SigmaY_RBV', dtype=float, read_only=True)
    sigma = pvproperty(name=':Sigma_RBV', dtype=float, read_only=True)

    ts_acquiring = pvproperty(name=':TSAcquiring', dtype=bool)
    ts_centroid_x = pvproperty(name=':TSCentroidX', dtype=float)
    ts_centroid_y = pvproperty(name=':TSCentroidY', dtype=float)
    ts_control = pvproperty(name=':TSControl', dtype=float)
    ts_current_point = pvproperty(name=':TSCurrentPoint', dtype=float)
    ts_max_value = pvproperty(name=':TSMaxValue', dtype=float)
    ts_max_x = pvproperty(name=':TSMaxX', dtype=float)
    ts_max_y = pvproperty(name=':TSMaxY', dtype=float)
    ts_mean_value = pvproperty(name=':TSMeanValue', dtype=float)
    ts_min_value = pvproperty(name=':TSMinValue', dtype=float)
    ts_min_x = pvproperty(name=':TSMinX', dtype=float)
    ts_min_y = pvproperty(name=':TSMinY', dtype=float)
    ts_net = pvproperty(name=':TSNet', dtype=float)
    ts_num_points = pvproperty(name=':TSNumPoints', dtype=int)
    ts_read = pvproperty(name=':TSRead', dtype=bool)
    ts_sigma_xy = pvproperty(name=':TSSigmaXY_RBV', dtype=float, read_only=True)
    ts_sigma_x = pvproperty(name=':TSSigmaX_RBV', dtype=float, read_only=True)
    ts_sigma_y = pvproperty(name=':TSSigmaY_RBV', dtype=float, read_only=True)
    ts_sigma = pvproperty(name=':TSSigma_RBV', dtype=float, read_only=True)
    ts_total = pvproperty(name=':TSTotal', dtype=float)
    total = pvproperty(name=':Total_RBV', dtype=float, read_only=True)


# Add some code to start a version of the server if this file is 'run'.
if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="StatsPlugin",
        desc=dedent(StatsPlugin.__doc__))
    ioc = StatsPlugin(**ioc_options)
    run(ioc.pvdb, **run_options)
