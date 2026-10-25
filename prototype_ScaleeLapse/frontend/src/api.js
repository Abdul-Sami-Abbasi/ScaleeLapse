let csrf = "";
export async function api(path, options = {}) {
  const method = options.method || "GET";
  if (method !== "GET") {
    const r = await fetch("/api/auth/csrf/", { credentials: "include" });
    csrf = (await r.json()).csrfToken;
  }
  const headers = {
    ...(options.body instanceof FormData
      ? {}
      : { "Content-Type": "application/json" }),
    ...(method !== "GET" ? { "X-CSRFToken": csrf } : {}),
    ...options.headers,
  };
  const response = await fetch("/api/" + path, {
    ...options,
    credentials: "include",
    headers,
    body:
      options.body instanceof FormData
        ? options.body
        : options.body
          ? JSON.stringify(options.body)
          : undefined,
  });
  if (response.status === 204) return null;
  const data = await response
    .json()
    .catch(() => ({ detail: "The server could not complete the request." }));
  if (!response.ok)
    throw new Error(
      typeof data === "string"
        ? data
        : Array.isArray(data)
          ? data.join(" ")
          : Object.entries(data)
              .map(
                ([k, v]) =>
                  `${k === "detail" ? "" : k + ": "}${Array.isArray(v) ? v.join(" ") : typeof v === "object" ? JSON.stringify(v) : v}`,
              )
              .join(" "),
    );
  return data;
}
