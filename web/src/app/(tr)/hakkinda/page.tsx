import { ContentView, contentMetadata } from "@/views/Content";

export const metadata = contentMetadata("tr", "about");

export default function Page() {
  return <ContentView lang="tr" page="about" />;
}
