import {Format} from "../../Format.js";

export class theLearningCompanyAssetsContainer extends Format
{
	name           = "The Learning Company assets container";
	ext            = [".grp"];
	forbidExtMatch = true;
	magic          = ["The Learning Company assets container", /^geArchive: GRP_RGRP( |$)/];
	converters     = ["gameextractor[codes:GRP_RGRP]"];
}
