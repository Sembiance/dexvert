program dfm2txt;

{$APPTYPE CONSOLE}

uses
  SysUtils,
  Classes;

var ASrcS, ADestS: TFileStream;
begin
  IF ParamCount() < 3 then
  begin
    WriteLn('Usage: dfm2txt res|bin <in.dfm> <out.txt>');
    Exit;
  end;

  ASrcS := TFileStream.Create(ParamStr(2), fmOpenRead);
  ADestS := TFileStream.Create(ParamStr(3), fmCreate);
  IF ParamStr(1) = 'bin' then
    ObjectBinaryToText(ASrcS, ADestS)
  else
    ObjectResourceToText(ASrcS, ADestS);

  ASrcS.Free;
  ADestS.Free;
end.
