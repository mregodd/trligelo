import type { NextConfig } from "next";

// Static export: `next build` writes plain HTML/CSS/JS to out/, served by Cloudflare Pages.
const config: NextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  reactStrictMode: true,
};

export default config;
