import client from "./client";

export const getCalls      = (params) => client.get("/calls/", { params });
export const registerCall  = (data)   => client.post("/calls/", data);
export const simulateCall  = (data)   => client.post("/calls/simulate", data || {});

