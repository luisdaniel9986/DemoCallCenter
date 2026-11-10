import client from "./client";

export const getDashboardMetrics    = () => client.get("/dashboard/metrics");
export const getPendingFollowups    = () => client.get("/dashboard/pending-followups");
export const getCustomerSummary     = () => client.get("/dashboard/customer-summary");

export const getCallsPerDay             = () => client.get("/dashboard/calls-per-day");
export const getCallOutcomes            = () => client.get("/dashboard/call-outcomes");
export const getCustomersByStatus       = () => client.get("/dashboard/customers-by-status");
export const getPredictionsByClass      = () => client.get("/dashboard/predictions-by-class");
export const getProbabilityDistribution = () => client.get("/dashboard/probability-distribution");
export const getPriorityCustomers       = () => client.get("/dashboard/priority-customers");
