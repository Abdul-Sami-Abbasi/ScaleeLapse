import React from "react";
import {
  render,
  screen,
  fireEvent,
  waitFor,
  cleanup,
} from "@testing-library/react";
import { it, expect, vi, afterEach } from "vitest";
vi.mock("./api", () => ({ api: vi.fn() }));
import { api } from "./api";
import { Auth, CreatePost, Results, PostDetail } from "./main";
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

it("retains the planned instant when editing only a draft caption", async () => {
  const post = {
    id: 9,
    title: "Synthetic scheduled post",
    caption: "Original caption",
    status: "DRAFT",
    creator: 1,
    brand_name: "Test brand",
    platform: "INSTAGRAM",
    scheduled_at: "2027-03-08T09:30:00Z",
    analyses: {},
    approvals: [],
  };
  api.mockResolvedValueOnce(post);
  render(
    <PostDetail
      post={post}
      user={{ id: 1, role: "OWNER" }}
      run={(fn) => fn()}
      busy={false}
      setSelected={vi.fn()}
      brands={[]}
    />,
  );
  fireEvent.click(screen.getByRole("button", { name: "Edit draft" }));
  fireEvent.change(screen.getByLabelText("Caption"), {
    target: { value: "Edited caption" },
  });
  fireEvent.submit(
    screen.getByRole("button", { name: "Save changes" }).closest("form"),
  );
  await waitFor(() =>
    expect(api).toHaveBeenCalledWith("posts/9/", {
      method: "PATCH",
      body: {
        title: post.title,
        caption: "Edited caption",
        scheduled_at: "2027-03-08T09:30:00.000Z",
      },
    }),
  );
});
it("signs in through the form and surfaces authentication errors", async () => {
  const onAuth = vi.fn();
  api.mockRejectedValueOnce(new Error("Invalid username or password."));
  render(<Auth onAuth={onAuth} />);
  fireEvent.change(screen.getByLabelText("Username"), {
    target: { value: "test.user" },
  });
  fireEvent.change(screen.getByLabelText("Password"), {
    target: { value: "TestFixture!123" },
  });
  fireEvent.submit(
    screen.getByRole("button", { name: "Sign in" }).closest("form"),
  );
  await screen.findByRole("alert");
  expect(onAuth).not.toHaveBeenCalled();
  expect(screen.getByRole("alert")).toHaveTextContent("Invalid username");
  api.mockResolvedValueOnce({ username: "test.user" });
  fireEvent.submit(
    screen.getByRole("button", { name: "Sign in" }).closest("form"),
  );
  await waitFor(() =>
    expect(onAuth).toHaveBeenCalledWith({ username: "test.user" }),
  );
});
it("prevents analyze without an image and permits saving a draft", () => {
  render(
    <CreatePost
      brands={[{ id: 1, name: "SYNTHETIC TEST" }]}
      run={vi.fn()}
      busy={false}
      onDone={vi.fn()}
    />,
  );
  expect(screen.getByRole("button", { name: "Analyze post" })).toBeDisabled();
  expect(screen.getByRole("button", { name: "Save draft" })).toBeEnabled();
});
it("does not render an invented score or toxicity clearance when evidence is absent", () => {
  render(
    <Results
      analyses={{
        visual_analysis: {
          score: null,
          palette: [],
          warnings: ["Brand Kit required"],
          logo: { status: "NOT_EVALUATED", reason: "Weights required" },
          fonts: { status: "MANUAL_REVIEW", reason: "Manual" },
          design_fatigue: {},
        },
        ai_suggestion: {
          status: "MODEL_REQUIRED",
          hashtags: [],
          notice: "Keyword suggestions only",
        },
        compliance_result: {
          level: "LOW",
          rules_checked: 0,
          coverage: "NO_SOURCED_RULES",
          findings: [],
          toxicity: "NOT_EVALUATED",
          disclaimer: "Not a guarantee of compliance.",
        },
      }}
    />,
  );
  expect(screen.getByText("—")).toBeInTheDocument();
  expect(screen.getByText(/NO SOURCED RULES/)).toBeInTheDocument();
  expect(
    screen.getByText("Not a guarantee of compliance."),
  ).toBeInTheDocument();
});
