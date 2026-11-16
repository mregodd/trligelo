import { ContentView, contentMetadata } from "@/views/Content";

export const metadata = contentMetadata("en", "about");

export default function Page() {
  return <ContentView lang="en" page="about" />;
}
