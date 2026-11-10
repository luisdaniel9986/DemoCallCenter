import client from "./client";

export const getFollowUps    = (params) => client.get("/followups/", { params });
export const createFollowUp  = (data)   => client.post("/followups/", data);
export const updateFollowUp  = (id, data) => client.put(`/followups/${id}`, data);
export const deleteFollowUp  = (id)     => client.delete(`/followups/${id}`);

