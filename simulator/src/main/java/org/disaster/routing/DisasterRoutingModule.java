package org.disaster.routing;

import org.matsim.core.controler.AbstractModule;
import org.matsim.simwrapper.SimWrapper;

public class DisasterRoutingModule extends AbstractModule {
    @Override
    public void install() {
        SimWrapper.addDashboardBinding(binder()).toInstance(new DisasterRoutingDashboard());
    }
}
