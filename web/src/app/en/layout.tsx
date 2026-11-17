import { Frame } from "@/components/Frame";
import { openGraph } from "@/lib/site";

export const metadata = { openGraph: openGraph("en") };

export default function Layout({ children }: { children: React.ReactNode }) {
  return <Frame lang="en">{children}</Frame>;
}
