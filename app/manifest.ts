import type { MetadataRoute } from "next";

export const dynamic = "force-static";
import { site } from "@/lib/site";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: site.name,
    short_name: "Apollo",
    description: site.description,
    start_url: "/",
    display: "standalone",
    background_color: "#F7F4EC",
    theme_color: "#14452F",
    icons: [{ src: "/icon.svg", sizes: "any", type: "image/svg+xml" }],
  };
}
