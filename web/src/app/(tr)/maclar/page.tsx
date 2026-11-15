import { MatchesView, matchesMetadata } from "@/views/Matches";

export const metadata = matchesMetadata("tr");

export default function Page() {
  return <MatchesView lang="tr" />;
}
