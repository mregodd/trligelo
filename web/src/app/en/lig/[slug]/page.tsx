import { LeagueView, leagueMetadata, leagueParams } from "@/views/League";

type Params = { params: Promise<{ slug: string }> };

export const generateStaticParams = leagueParams;

export async function generateMetadata({ params }: Params) {
  return leagueMetadata("en", (await params).slug);
}

export default async function Page({ params }: Params) {
  return <LeagueView lang="en" slug={(await params).slug} />;
}
