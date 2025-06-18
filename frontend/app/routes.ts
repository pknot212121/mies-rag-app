import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/login.tsx"),
  route("register", "routes/register.tsx"),

  route("dashboard", "routes/dashboard.tsx", [
    index("routes/jobCreate.tsx"),
    route("job/:id", "routes/jobDetails.tsx"),
  ]),
] satisfies RouteConfig;

