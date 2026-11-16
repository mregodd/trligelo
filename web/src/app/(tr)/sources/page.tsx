import { ContentView, contentMetadata } from "@/views/Content";

export const metadata = contentMetadata("tr", "sources");

export default function Page() {
  return <ContentView lang="tr" page="sources" />;
}
