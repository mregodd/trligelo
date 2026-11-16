import { ContentView, contentMetadata } from "@/views/Content";

export const metadata = contentMetadata("tr", "privacy");

export default function Page() {
  return <ContentView lang="tr" page="privacy" />;
}
