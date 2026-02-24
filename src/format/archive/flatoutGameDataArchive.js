import {Format} from "../../Format.js";

export class flatoutGameDataArchive extends Format
{
	name           = "Flatout game data archive";
	ext            = [".bfs"];
	forbidExtMatch = true;
	magic          = ["Flatout game data archive", /^geArchive: (BFS_BFS1|BFS)( |$)/];
	converters     = ["gameextractor[codes:BFS_BFS1,BFS]"];
}
