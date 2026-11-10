import { useEffect, useState } from "react";
import {
  getDashboardMetrics, getPendingFollowups, getCallsPerDay, getCallOutcomes,
  getCustomersByStatus, getPredictionsByClass, getProbabilityDistribution, getPriorityCustomers,
} from "../api/dashboard";
import MetricsRow            from "../components/dashboard/MetricsRow";
import DashboardCharts       from "../components/dashboard/DashboardCharts";
import PendingFollowupsTable from "../components/dashboard/PendingFollowupsTable";
import LoadingSpinner        from "../components/ui/LoadingSpinner";

export default function Dashboard() {
  const [metrics,   setMetrics]   = useState(null);
  const [followups, setFollowups] = useState([]);
  const [charts,    setCharts]    = useState(null);
  const [loading,   setLoading]   = useState(true);

  useEffect(() => {
    Promise.all([
      getDashboardMetrics(), getPendingFollowups(), getCallsPerDay(), getCallOutcomes(),
      getCustomersByStatus(), getPredictionsByClass(), getProbabilityDistribution(), getPriorityCustomers(),
    ])
      .then(([m, f, perDay, outcomes, byStatus, byClass, distribution, priority]) => {
        setMetrics(m.data);
        setFollowups(f.data);
        setCharts({
          callsPerDay: perDay.data, outcomes: outcomes.data, byStatus: byStatus.data,
          byClass: byClass.data, distribution: distribution.data, priority: priority.data,
        });
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner message="Cargando dashboard..." />;

  return (
    <div className="space-y-6">
      <MetricsRow metrics={metrics} />
      {charts && <DashboardCharts data={charts} />}
      <PendingFollowupsTable followups={followups} />
    </div>
  );
}
