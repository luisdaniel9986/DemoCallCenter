import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/layout/Layout";
import Dashboard from "./pages/Dashboard";
import CallCenter from "./pages/CallCenter";
import Customers from "./pages/Customers";
import CustomerDetail from "./pages/CustomerDetail";
import CallHistory from "./pages/CallHistory";
import FollowUps from "./pages/FollowUps";
import Predictions from "./pages/Predictions";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="call-center" element={<CallCenter />} />
          <Route path="customers" element={<Customers />} />
          <Route path="customers/:id" element={<CustomerDetail />} />
          <Route path="calls" element={<CallHistory />} />
          <Route path="followups" element={<FollowUps />} />
          <Route path="predictions" element={<Predictions />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
