import { apiRequest } from "./client";
import type { Camera, CameraPayload } from "../types/camera";

export function listCameras(token: string): Promise<Camera[]> {
  return apiRequest<Camera[]>("/cameras", { token });
}

export function createCamera(token: string, payload: CameraPayload): Promise<Camera> {
  return apiRequest<Camera>("/cameras", {
    method: "POST",
    token,
    body: JSON.stringify(payload),
  });
}
