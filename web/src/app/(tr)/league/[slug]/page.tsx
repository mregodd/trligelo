import { LeagueView, leagueMetadata, leagueParams } from "@/views/League";

type Params = { params: Promise<{ slug: string }> };

export const generateStaticParams = leagueParams;

export async function generateMetadata({ params }: Params) {
  return leagueMetadata("tr", (await params).slug);
}

export default async function Page({ params }: Params) {
  return <LeagueView lang="tr" slug={(await params).slug} />;
}
