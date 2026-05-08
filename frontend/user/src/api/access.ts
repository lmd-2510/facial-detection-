import { apiRequest } from "./client";
import type { AccessCheckPayload, AccessCheckResponse } from "../types/access";

export function checkAccess(
  token: string,
  payload: AccessCheckPayload,
): Promise<AccessCheckResponse> {
  return apiRequest<AccessCheckResponse>("/access/check", {
    method: "POST",
    token,
    body: JSON.stringify(payload),
  });
}
