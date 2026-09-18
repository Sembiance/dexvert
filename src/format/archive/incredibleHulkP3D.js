import {Format} from "../../Format.js";

export class incredibleHulkP3D extends Format
{
	name           = "The Incredible Hulk P3D archive";
	ext            = [".p3d"];
	forbidExtMatch = true;
	magic          = [/^geArchive: P3D_P3D( |$)/];
	converters     = ["gameextractor[codes:P3D_P3D]"];
}
