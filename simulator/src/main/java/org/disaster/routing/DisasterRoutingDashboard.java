package org.disaster.routing;

import org.disaster.routing.analysis.TripPurposeBy10Min;
import org.disaster.routing.analysis.TripStatsDisaster;
import org.matsim.application.analysis.population.TripAnalysis;
import org.matsim.application.analysis.traffic.TrafficAnalysis;
import org.matsim.application.prepare.network.CreateAvroNetwork;
import org.matsim.simwrapper.Dashboard;
import org.matsim.simwrapper.Header;
import org.matsim.simwrapper.Layout;
import org.matsim.simwrapper.viz.ColorScheme;
import org.matsim.simwrapper.viz.MapPlot;
import org.matsim.simwrapper.viz.Plotly;
import org.matsim.simwrapper.viz.Table;
import tech.tablesaw.plotly.components.Axis;
import tech.tablesaw.plotly.traces.BarTrace;

import java.util.List;

public class DisasterRoutingDashboard implements Dashboard {
    @Override
    public void configure(Header header, Layout layout) {
        header.title = "Disaster Evacuation Routing Dashboard";

        layout.row("traffic_volume").el(MapPlot.class, (viz, data) -> {
            viz.title = "Simulated traffic volume";
            viz.center = data.context().getCenter();
            viz.zoom = data.context().mapZoomLevel;
            viz.height = 7.5;
            viz.width = 2.0;

            viz.setShape(data.compute(CreateAvroNetwork.class, "network.avro", "--with-properties"), "linkId");
            viz.addDataset("traffic", data.compute(TrafficAnalysis.class, "traffic_stats_by_link_daily.csv"));

            viz.display.lineColor.dataset = "traffic";
            viz.display.lineColor.columnName = "simulated_traffic_volume";
            viz.display.lineColor.join = "link_id";
            viz.display.lineColor.setColorRamp(ColorScheme.RdYlBu, 5, true);

            viz.display.lineWidth.dataset = "traffic";
            viz.display.lineWidth.columnName = "simulated_traffic_volume";
            viz.display.lineWidth.scaleFactor = 20000d;
            viz.display.lineWidth.join = "link_id";
        });

        layout.row("statistics", header.tab)
                .el(Table.class, (viz, data) -> {
                    viz.title = "Evacuation Statistics";
                    viz.dataset = data.compute(TripStatsDisaster.class, "trip_stats.csv");
                    viz.showAllRows = true;
                })
                .el(Plotly.class, (viz, data) -> {
                    viz.title = "Trip distance distribution";
                    viz.colorRamp = ColorScheme.Viridis;

                    viz.addTrace(BarTrace.builder(Plotly.OBJ_INPUT, Plotly.INPUT).name("Simulated").build(),
                            viz.addDataset(data.compute(TripAnalysis.class, "mode_share.csv"))
                                    .aggregate(List.of("dist_group"), "share", Plotly.AggrFunc.SUM)
                                    .mapping()
                                    .x("dist_group")
                                    .y("share")
                    );
                });

        createTripDataRow(layout, "departures", header.tab, "Departures", "departure");
        createTripDataRow(layout, "arrivals", header.tab, "Arrivals", "arrival");
    }

    private static void createTripDataRow(Layout layout, String dataType, String tab, String chartTitle, String metric) {
        layout.row(dataType, tab).el(Plotly.class, (viz, data) -> {
            viz.title = chartTitle;
            viz.description = "by 10-minute intervals";
            viz.layout = tech.tablesaw.plotly.components.Layout.builder()
                    .xAxis(Axis.builder().title("Time (minutes)").build())
                    .yAxis(Axis.builder().title("Trips").build())
                    .barMode(tech.tablesaw.plotly.components.Layout.BarMode.STACK)
                    .build();

            viz.addTrace(BarTrace.builder(Plotly.OBJ_INPUT, Plotly.INPUT).build(),
                    viz.addDataset(data.compute(TripPurposeBy10Min.class, "trip_purposes_by_10_minutes.csv")).mapping()
                            .name("purpose", ColorScheme.Spectral)
                            .x("bin")
                            .y(metric)
            );
        });
    }
}
