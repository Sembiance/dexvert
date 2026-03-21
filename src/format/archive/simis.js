import {Format} from "../../Format.js";

export class simis extends Format
{
	name             = "Simis Archive";
	ext              = [".s", ".ace", ".t", ".dat", ".mis", ".rtc", ".a", ".t"];
	forbidExtMatch   = true;
	magic            = ["Simis format", /^geArchive: ACE_SIMIS( |$)/];
	confidenceAdjust = () => -10;	// Reduce by 10 so that image/aceTexture and poly/simisShape match first
	converters       = ["gameextractor[codes:ACE_SIMIS][renameOut]"];
}
