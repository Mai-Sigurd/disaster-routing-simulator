package org.disaster.routing.simwrapper.viz;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * The Tile plug-in creates an overview of important key figures.
 */
public class Tile extends Viz {

	/**
	 * The filepath containing the data.
	 */
	@JsonProperty(required = true)
	public String dataset;

	public Tile() {
		super("tile");
	}
}
