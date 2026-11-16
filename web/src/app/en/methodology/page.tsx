import { MethodologyView, methodologyMetadata } from "@/views/Methodology";

export const metadata = methodologyMetadata("en");

export default function Page() {
  return <MethodologyView lang="en" />;
}
