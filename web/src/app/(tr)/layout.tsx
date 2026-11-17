import { Frame } from "@/components/Frame";
import { openGraph } from "@/lib/site";

export const metadata = { openGraph: openGraph("tr") };

export default function Layout({ children }: { children: React.ReactNode }) {
  return <Frame lang="tr">{children}</Frame>;
}
