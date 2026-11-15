import { ContentView, contentMetadata } from "@/views/Content";

export const metadata = contentMetadata("en", "sources");

export default function Page() {
  return <ContentView lang="en" page="sources" />;
}
