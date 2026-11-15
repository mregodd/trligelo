import { HomeView, homeMetadata } from "@/views/Home";

export const metadata = homeMetadata("tr");

export default function Page() {
  return <HomeView lang="tr" />;
}
