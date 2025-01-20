program fcut;

uses
  SysUtils,
  Classes;

procedure CutFile(const SourceFile: string; StartPos, Length: Integer; const OutputFile: string);
var
  InputStream: TFileStream;
  OutputStream: TFileStream;
begin
  // Open the source file for reading
  InputStream := TFileStream.Create(SourceFile, fmOpenRead or fmShareDenyWrite);
  try
    // Check if start position is valid
    if (StartPos < 0) or (StartPos >= InputStream.Size) then
      raise Exception.Create('Invalid start position.');

    // Adjust length if it goes beyond the file size
    if (StartPos + Length > InputStream.Size) then
      Length := InputStream.Size - StartPos;

    // Create the output file
    OutputStream := TFileStream.Create(OutputFile, fmCreate);
    try
      // Seek to the start position and copy the specified length
      InputStream.Position := StartPos;
      if Length <> 0 then
        OutputStream.CopyFrom(InputStream, Length)
      else
        OutputStream.CopyFrom(InputStream, InputStream.Size - StartPos);
    finally
      OutputStream.Free;
    end;
  finally
    InputStream.Free;
  end;
end;

var
  SourceFile, OutputFile: string;
  StartPos, Length: Integer;
begin
  // Check for the correct number of parameters
  if ParamCount < 2 then
  begin
    Writeln('Usage: fcut <SourceFile> <StartPosition> [Length] [OutputFile]');
    Exit;
  end;

  // Get the parameters
  SourceFile := ParamStr(1);
  StartPos := StrToInt(ParamStr(2)) - 1; // starts from zero actually
  if StartPos < 0 then
  begin
    Writeln('Invalid StartPostion.');
    Exit;
  end;

  // Determine output file name
  if ParamCount < 3 then
    Length := 0
  else
    Length := StrToInt(ParamStr(3));

  if ParamCount >= 4 then
    OutputFile := ParamStr(4)
  else
    OutputFile := ChangeFileExt(SourceFile, '') + '_fragment' + ExtractFileExt(SourceFile);

  try
    // Cut the file
    CutFile(SourceFile, StartPos, Length, OutputFile);
    Writeln('Successfully cut the file to: ', OutputFile);
  except
    on E: Exception do
      Writeln('Error: ', E.Message);
  end;
end.
