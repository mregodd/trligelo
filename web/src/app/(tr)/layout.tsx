import { Frame } from "@/components/Frame";

export default function Layout({ children }: { children: React.ReactNode }) {
  return <Frame lang="tr">{children}</Frame>;
}
