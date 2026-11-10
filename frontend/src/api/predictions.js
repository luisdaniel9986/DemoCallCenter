import client from "./client";

export const getPredictions   = (params) => client.get("/predictions/", { params });
export const createPrediction = (data)   => client.post("/predictions/", data);

