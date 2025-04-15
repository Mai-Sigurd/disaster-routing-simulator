package org.disaster.routing.analysis;

import it.unimi.dsi.fastutil.doubles.DoubleArrayList;
import it.unimi.dsi.fastutil.doubles.DoubleList;

import org.matsim.api.core.v01.Id;
import org.matsim.api.core.v01.Coord;
import org.matsim.api.core.v01.network.Link;
import org.matsim.api.core.v01.network.Network;
import org.matsim.core.network.NetworkUtils;
import org.matsim.core.router.util.TravelTime;


import javax.annotation.Nullable;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * Class to calculate the traffic congestion index based on the paper
 * "A Traffic Congestion Assessment Method for Urban Road Networks Based on Speed Performance Index" by Feifei He, Xuedong Yan, Yang Liu, Lu Ma.
 */
public final class TrafficStatsCalculatorDisaster {

	private final Network network;
	private final TravelTime travelTime;

	private final int timeSlice;

	public TrafficStatsCalculatorDisaster(Network network, TravelTime travelTime, int timeSlice) {
		this.network = network;
		this.travelTime = travelTime;
		this.timeSlice = timeSlice;
	}

	/**
	 * Calculates the speed performance index, which is the ratio of actual travel time and free speed travel time.
	 */
	public double getSpeedPerformanceIndex(Link link, double time) {

		double length = link.getLength();

		double allowedSpeed = NetworkUtils.getAllowedSpeed(link);

		double actualTravelTime = travelTime.getLinkTravelTime(link, time, null, null);

		double actualSpeed = length / actualTravelTime;

		double ratio = actualSpeed / allowedSpeed;

		return ratio > 1 ? 1 : ratio;
	}

	public double getSpeedPerformanceIndex(Link link, int startTime, int endTime) {
		DoubleList indices = new DoubleArrayList();

		for (int time = startTime; time < endTime; time += timeSlice)
			indices.add(
					this.getSpeedPerformanceIndex(link, time)
			);

		return indices.doubleStream().average().orElse(-1);
	}

	public Coord[] getLinkCoordinates(Link link, int amountOfCoords) {
		var coords = new Coord[amountOfCoords];
		// Linear interpolation
		for (int i = 0; i < amountOfCoords; i++) {
			double ratio = (double) i / (amountOfCoords-1);
			coords[i] = new Coord(
					link.getFromNode().getCoord().getX() * (1 - ratio) + link.getToNode().getCoord().getX() * ratio,
					link.getFromNode().getCoord().getY() * (1 - ratio) + link.getToNode().getCoord().getY() * ratio
			);
		}
		return coords;
	}

	//Divides the day in intervals in seconds with the duration of intervalInSeconds
	public List<Time> generateTimes(int intervalInSeconds)
	{
		List<Time> times = new ArrayList<>();

		int secondsInDay = 24 * 60 * 60; // 86400 seconds in a day

		for (int start = 0; start < secondsInDay; start += intervalInSeconds) {
			int end = Math.min(start + intervalInSeconds, secondsInDay);
			times.add(new Time(start, end));
		}

		return times;
	}

	//Calculate congestion across time for all links
	public List<XYTimeValue> calculateCongestionAcrossTimeAndLinks() {

		List<Time> times = generateTimes(600);
		List<XYTimeValue> xYTimeValues = new ArrayList<XYTimeValue>();

		for (Map.Entry<Id<Link>, ? extends Link> entry : this.network.getLinks().entrySet()) {
			Link link = entry.getValue();

			for (Time time : times) {
				double val = getSpeedPerformanceIndex(link, time.start, time.end);

				Coord[] coords = getLinkCoordinates(link, 5);

				for (Coord coord : coords) {
					xYTimeValues.add(new XYTimeValue(time.start, coord.getX(), coord.getY(), val));
				}
			} 	
		}
		return xYTimeValues;
	}


	/**
	 * Calculates the congestion index based on the ratio of actual travel time and free speed travel time.
	 */
	public double getLinkCongestionIndex(Link link, int startTime, int endTime) {

		DoubleList speedPerformance = new DoubleArrayList();

		int congestedPeriodCounter = 0;
		int totalObservedPeriods = 0;

		for (int time = startTime; time < endTime; time += timeSlice) {

			double speedPerformanceIndex = this.getSpeedPerformanceIndex(link, time);
			speedPerformance.add(speedPerformanceIndex);

			if (speedPerformanceIndex <= 0.5)
				congestedPeriodCounter++;

			totalObservedPeriods++;
		}

		double averageSpeedPerformance = speedPerformance.doubleStream().average().orElse(-1);

		return averageSpeedPerformance * (1 - (double) congestedPeriodCounter / totalObservedPeriods);
	}

	/**
	 * Calculates the network congestion index for a given time period. Can be done for a certain road type.
	 */
	public double getNetworkCongestionIndex(int startTime, int endTime, @Nullable String roadType) {

		double sumOfLinkLengthMultipiesLinkCongestionIndex = 0.0;
		double sumLinkLength = 0.0;

		for (Map.Entry<Id<Link>, ? extends Link> entry : this.network.getLinks().entrySet()) {
			Link link = entry.getValue();

			String type = NetworkUtils.getHighwayType(link);
			if (roadType != null && !type.equals(roadType))
				continue;

			double linkCongestionIndex = getLinkCongestionIndex(link, startTime, endTime);

			double length = link.getLength() * link.getNumberOfLanes();

			sumOfLinkLengthMultipiesLinkCongestionIndex += length * linkCongestionIndex;
			sumLinkLength += length;
		}

		return sumOfLinkLengthMultipiesLinkCongestionIndex / sumLinkLength;
	}

	/**
	 * Calculates the avg speed for a given link and time interval in meter per seconds.
	 */
	public double getAvgSpeed(Link link, int startTime, int endTime) {

		DoubleList speeds = new DoubleArrayList();

		for (int time = startTime; time < endTime; time += timeSlice) {

			double seconds = this.travelTime.getLinkTravelTime(link, time, null, null);
			speeds.add(link.getLength() / seconds);
		}

		return speeds.doubleStream().average().orElse(-1);
	}

	public class Time {
		public int start;
		public int end;
	
		public Time(int start, int end) {
			this.start = start;
			this.end = end;
		}
	}

	record XYTimeValue(double time, double x, double y, double value) { }
}
