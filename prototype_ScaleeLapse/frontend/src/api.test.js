import { it, expect, vi, afterEach } from "vitest";
import { api } from "./api";
afterEach(() => vi.unstubAllGlobals());
it("gets a CSRF token and includes it with state-changing requests", async () => {
  const fetch = vi
    .fn()
    .mockResolvedValueOnce({ json: async () => ({ csrfToken: "test-token" }) })
    .mockResolvedValueOnce({
      ok: true,
      status: 201,
      json: async () => ({ id: 1 }),
    });
  vi.stubGlobal("fetch", fetch);
  expect(
    await api("posts/", { method: "POST", body: { title: "Test" } }),
  ).toEqual({ id: 1 });
  expect(fetch.mock.calls[1][1].headers["X-CSRFToken"]).toBe("test-token");
  expect(fetch.mock.calls[1][1].credentials).toBe("include");
});
it("turns API validation errors into readable messages", async () => {
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValue({
        ok: false,
        status: 400,
        json: async () => ({ caption: ["This field is required."] }),
      }),
  );
  await expect(api("posts/")).rejects.toThrow(
    "caption: This field is required.",
  );
});
it("handles a successful deletion without parsing an empty response", async () => {
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValueOnce({ json: async () => ({ csrfToken: "token" }) })
      .mockResolvedValueOnce({ ok: true, status: 204 }),
  );
  expect(await api("posts/1/", { method: "DELETE" })).toBeNull();
});
