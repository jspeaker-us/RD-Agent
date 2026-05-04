import qlib


def main():
    qlib.init(provider_uri="~/.qlib/qlib_data/cn_data")

    from qlib.data import D

    instruments = D.instruments()
    fields = ["$open", "$close", "$high", "$low", "$volume", "$factor"]
    data = D.features(instruments, fields, freq="day").swaplevel().sort_index().loc["2008-12-29":].sort_index()

    data.to_hdf("./daily_pv_all.h5", key="data")

    debug_data = D.features(instruments, fields, start_time="2018-01-01", end_time="2019-12-31", freq="day").swaplevel().sort_index()
    debug_instruments = debug_data.index.get_level_values("instrument").unique()
    selected_instruments = [inst for inst in data.reset_index()["instrument"].unique() if inst in debug_instruments][:100]
    data = debug_data.swaplevel().loc[selected_instruments].swaplevel().sort_index()

    data.to_hdf("./daily_pv_debug.h5", key="data")


if __name__ == "__main__":
    main()
