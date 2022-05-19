import {Format} from "../../Format.js";

export class timeworksPublisher extends Format
{
	name           = "Timeworks Publisher/Publish It!";
	ext            = [".dtp"];
	forbidExtMatch = true;
	magic          = ["Timeworks Publisher"];
	notes          = "All I could find on it: https://sparcie.wordpress.com/2018/01/22/open-access-for-dos/  It may be related to Greenstreet Publisher, see that.";
	converters     = ["strings"];
}
