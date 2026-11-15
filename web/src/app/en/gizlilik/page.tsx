import { ContentView, contentMetadata } from "@/views/Content";

export const metadata = contentMetadata("en", "privacy");

export default function Page() {
  return <ContentView lang="en" page="privacy" />;
}
