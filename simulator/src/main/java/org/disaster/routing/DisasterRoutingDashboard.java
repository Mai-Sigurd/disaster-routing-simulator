package org.disaster.routing;

import org.disaster.routing.analysis.PeopleInSafetyXY;
import org.disaster.routing.analysis.TrafficAnalysisDisaster;
import org.disaster.routing.analysis.TripPurposeBy10Min;
import org.disaster.routing.analysis.TripStatsDisaster;
import org.matsim.api.core.v01.TransportMode;
import org.matsim.application.analysis.population.TripAnalysis;
import org.matsim.application.prepare.network.CreateAvroNetwork;
import org.matsim.simwrapper.Dashboard;
import org.matsim.simwrapper.Header;
import org.matsim.simwrapper.Layout;
import org.matsim.simwrapper.viz.ColorScheme;
import org.matsim.simwrapper.viz.MapPlot;
import org.matsim.simwrapper.viz.Plotly;
import org.matsim.simwrapper.viz.Table;
import org.matsim.simwrapper.viz.XYTime;

import tech.tablesaw.plotly.components.Axis;
import tech.tablesaw.plotly.components.Line;
import tech.tablesaw.plotly.components.Marker;
import tech.tablesaw.plotly.traces.BarTrace;
import tech.tablesaw.plotly.traces.ScatterTrace;

import java.util.List;
import java.util.Set;

public class DisasterRoutingDashboard implements Dashboard {
    private final Set<String> modes;

    public DisasterRoutingDashboard() {
        this(Set.of(TransportMode.car));
    }

    public DisasterRoutingDashboard(Set<String> modes) {
        this.modes = modes;
    }

    private static void createTripDataRow(Layout layout, String dataType, String tab, String chartTitle, String metric, String xAxisTitle) {
        layout.row(dataType, tab).el(Plotly.class, (viz, data) -> {
            viz.title = chartTitle;
            viz.description = "by 10-minute intervals";
            viz.layout = tech.tablesaw.plotly.components.Layout.builder()
                    .xAxis(Axis.builder().title(xAxisTitle).build())
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

    private static void createTripDataViz(Layout layout, String rowId, String tab) {
        layout.row(rowId, tab).el(Plotly.class, (viz, data) -> {
            viz.title = "Departures and Arrivals";
            viz.description = "by 10-minute intervals";
            viz.layout = tech.tablesaw.plotly.components.Layout.builder()
                    .xAxis(Axis.builder().title("Time from start of simulation (minutes)").build())
                    .yAxis(Axis.builder().title("Trips").build())
                    .barMode(tech.tablesaw.plotly.components.Layout.BarMode.GROUP)
                    .build();

            Plotly.DataSet dataset = viz.addDataset(data.compute(TripPurposeBy10Min.class, "trip_purposes_by_10_minutes.csv"));

            viz.addTrace(BarTrace.builder(Plotly.OBJ_INPUT, Plotly.INPUT)
                            .name("Departures")
                            .marker(Marker.builder().color("#1f77b4").build())  // Blue color
                            .build(),
                    dataset.mapping()
                            .x("bin")
                            .y("departure")
            );

            viz.addTrace(BarTrace.builder(Plotly.OBJ_INPUT, Plotly.INPUT)
                            .name("Arrivals")
                            .marker(Marker.builder().color("#ff7f0e").build())  // Orange color
                            .build(),
                    dataset.mapping()
                            .x("bin")
                            .y("arrival")
            );
        });
    }

    @Override
    public void configure(Header header, Layout layout) {
        header.title = "Disaster Evacuation Routing Dashboard";

        layout.row("statistics", header.tab)
                .el(Table.class, (viz, data) -> {
                    viz.title = "Evacuation Statistics";
                    viz.dataset = data.compute(TripStatsDisaster.class, "trip_stats_disaster.csv");
                    viz.showAllRows = true;
                })
                .el(Table.class, (viz, data) -> {
                    viz.title = "Simulation Statistics";
                    viz.dataset = "analysis/danger_zone_data.csv";
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
        layout.row("population")
                .el(MapPlot.class, (viz, _) -> {
                    // Is overwritten in python project
                    viz.title = "Population density"";
                });

        // createTripDataRow(layout, "departures", header.tab, "Departures", "departure", "Time from start of simulation (minutes)");
        // createTripDataRow(layout, "arrivals", header.tab, "Arrivals", "arrival", "Time from start of simulation (minutes)");
        createTripDataViz(layout, "departure-arrival", header.tab);
        createTripDataRow(layout, "traveltype", header.tab, "Travel times", "traveltime", "Time from departure to arrival (minutes)");


        layout.row("Amount of people in safety").el(Plotly.class, ((viz, data) -> {
            viz.title = "People in safety";
            viz.description = "The fraction of people who have reached safety at time t";

            Plotly.DataSet ds = viz.addDataset(data.compute(PeopleInSafetyXY.class, "people_in_safety.csv"));

            viz.layout = tech.tablesaw.plotly.components.Layout.builder()
                    .xAxis(Axis.builder().title("Time from start of simulation (minutes)").build())
                    .yAxis(Axis.builder().title("Fraction of people in safety").build())
                    .build();

            viz.addTrace(ScatterTrace.builder(Plotly.INPUT, Plotly.INPUT)
                    .name("People in safety")
                    .mode(ScatterTrace.Mode.LINE)
                    .line(Line.builder().dash(Line.Dash.SOLID).build()).build(), ds.mapping()
                    .x("bin").y("cumulative_traveltime")
            );
        }));


        String[] args = new String[]{"--transport-modes", String.join(",", this.modes)};
        layout.row("index_by_hour").el(Plotly.class, (viz, data) -> {
                    viz.title = "Network congestion index";
                    viz.description = "by hour";

                    Plotly.DataSet ds = viz.addDataset(data.compute(TrafficAnalysisDisaster.class, "traffic_stats_by_road_type_and_hour.csv", args));

                    viz.layout = tech.tablesaw.plotly.components.Layout.builder()
                            .yAxis(Axis.builder().title("Index").build())
                            .xAxis(Axis.builder().title("Hour").build())
                            .barMode(tech.tablesaw.plotly.components.Layout.BarMode.OVERLAY)
                            .build();

                    viz.addTrace(ScatterTrace.builder(Plotly.INPUT, Plotly.INPUT).mode(ScatterTrace.Mode.LINE).build(), ds.mapping()
                            .x("hour")
                            .y("congestion_index")
                            .name("road_type", ColorScheme.Spectral)
                    );
                })
                .el(Table.class, ((viz, data) -> {
                    viz.title = "Traffic stats for all roads";

                    viz.dataset = data.compute(TrafficAnalysisDisaster.class, "traffic_stats_by_road_type_daily.csv", args);

                    viz.showAllRows = true;
                    viz.enableFilter = false;
                }));

        layout.row("map").el(MapPlot.class, (viz, data) -> {
            viz.title = "Simulated traffic volume";
            viz.center = data.context().getCenter();
            viz.zoom = data.context().mapZoomLevel;

            viz.setShape(data.compute(CreateAvroNetwork.class, "network.avro"), "id");

            viz.addDataset("traffic", data.compute(TrafficAnalysisDisaster.class, "traffic_stats_by_link_daily.csv"));

            viz.display.lineColor.dataset = "traffic";
            viz.display.lineColor.columnName = "avg_speed";
            viz.display.lineColor.join = "link_id";
            viz.display.lineColor.setColorRamp(ColorScheme.RdYlBu, 5, false);

            viz.display.lineWidth.dataset = "traffic";
            viz.display.lineWidth.columnName = "simulated_traffic_volume";
            viz.display.lineWidth.scaleFactor = 10d;
            viz.display.lineWidth.join = "link_id";

            viz.height = 12d;
        });

        layout.row("congestion_map").el(XYTime.class, (viz, data) -> {
            viz.title = "Congestion";
            String output = data.compute(TrafficAnalysisDisaster.class, "congestion.xyt.csv");
            viz.file = output;
            viz.height = 12d;
            viz.radius = 10.0;
        });
    }
}
