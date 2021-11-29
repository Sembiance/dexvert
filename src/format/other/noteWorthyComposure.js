import {Format} from "../../Format.js";

export class noteWorthyComposure extends Format
{
	name           = "NoteWorthy Composure";
	ext            = [".nw"];
	forbidExtMatch = true;
	magic          = ["NoteWorthy song"];
	converters     = ["strings"];
}
