import {Format} from "../../Format.js";

export class threeDUltraCoolDataFile extends Format
{
	name           = "3D Ultra Cool data file";
	ext            = [".tbv"];
	forbidExtMatch = true;
	magic          = ["3D Ultra Cool data file", /^geArchive: TBV_TBVOL( |$)/];
	converters     = ["gameextractor[codes:TBV_TBVOL]"];
}
