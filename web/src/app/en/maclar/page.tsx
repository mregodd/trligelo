import { MatchesView, matchesMetadata } from "@/views/Matches";

export const metadata = matchesMetadata("en");

export default function Page() {
  return <MatchesView lang="en" />;
}
