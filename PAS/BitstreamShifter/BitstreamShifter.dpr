program BitstreamShifter;

uses
  SysUtils, Classes;

function ShiftBitsRight(const InputBytes: TBytes; BitsToShift: Integer): TBytes;
var
  i: Integer;
begin
  if BitsToShift < 0 then
    raise Exception.Create('BitsToShift must be non-negative');

  SetLength(Result, Length(InputBytes)); // Prepare the result array
  if Length(InputBytes) = 0 then Exit; // Return if input is empty

  if Length(InputBytes) = 1 then
  begin
    Result[0] := InputBytes[0] shr BitsToShift;
    Exit;
  end;

  // Initialize the first byte of result
  Result[0] := 0;

  // Shift bits
  for i := 0 to Length(InputBytes) - 1 do
  begin
    // For the first byte, we need to handle bits differently
    if i = 0 then
    begin
      Result[0] := InputBytes[0] shr BitsToShift;
      if (InputBytes[0] and ((1 shl BitsToShift) - 1)) <> 0 then
        if (i + 1 < Length(InputBytes)) then
          Result[1] := (InputBytes[0] and 1) shl (8 - BitsToShift) // Set the first bit of the next byte if needed
        else
          Result[1] := 0; // If there is no next byte, just set it to 0
    end
    else
    begin
      // Shift the bits normally, carrying from the previous byte
      Result[i] := (InputBytes[i] shr BitsToShift) or ((InputBytes[i - 1] and ((1 shl BitsToShift) - 1)) shl (8 - BitsToShift));
    end;
  end;
end;

function ShiftBitsLeft(const InputBytes: TBytes; BitsToShift: Integer): TBytes;
var
  i: Integer;
begin
  if BitsToShift < 0 then
    raise Exception.Create('BitsToShift must be non-negative');

  SetLength(Result, Length(InputBytes)); // Prepare the result array
  if Length(InputBytes) = 0 then Exit; // Return if input is empty

  // Initialize the last byte of result
  Result[Length(InputBytes) - 1] := 0;

  {$R-}
  // Shift bits
  for i := Length(InputBytes) - 1 downto 0 do
  begin
    // For the last byte, we need to handle bits differently
    if i = Length(InputBytes) - 1 then
    begin
      Result[Length(InputBytes) - 1] := InputBytes[Length(InputBytes) - 1] shl BitsToShift;
      if (InputBytes[Length(InputBytes) - 1] and (255 shl (8 - BitsToShift))) <> 0 then
        if (i - 1 >= 0) then
          Result[Length(InputBytes) - 2] := (InputBytes[Length(InputBytes) - 1] and $FF) shr (8 - BitsToShift) // Set the last bit of the previous byte if needed
        else
          Result[Length(InputBytes) - 2] := 0; // If there is no previous byte, just set it to 0
    end
    else
    begin
      // Shift the bits normally, carrying from the next byte
      Result[i] := (InputBytes[i] shl BitsToShift) or (InputBytes[i + 1] shr (8 - BitsToShift));
    end;
  end;
  {$R+}
end;

procedure ShiftBitstream(const InputFile, OutputFile: string; ShiftValue: Integer);
var
  FileStream: TFileStream;
  InputBytes, OutputBytes: TBytes;
begin
  // Read the file into a byte array
  FileStream := TFileStream.Create(InputFile, fmOpenRead);
  try
    SetLength(InputBytes, FileStream.Size);
    FileStream.Read(InputBytes[0], FileStream.Size);
  finally
    FileStream.Free;
  end;

  // Shift bits to the right
  if ShiftValue > 0 then
    OutputBytes := ShiftBitsRight(InputBytes, ShiftValue);
  if ShiftValue < 0 then
    OutputBytes := ShiftBitsLeft(InputBytes, -ShiftValue);

  FileStream := TFileStream.Create(OutputFile, fmCreate);
  try
    FileStream.Write(OutputBytes[0], Length(OutputBytes));
  finally
    FileStream.Free;
  end;
end;

var
  InputFile, OutputFile: string;
  ShiftValue: Integer;
begin
  // Check if the correct number of parameters are provided
  if ParamCount <> 3 then
  begin
    Writeln('Usage: BitstreamShifter <inputFile> <outputFile> <shiftValue>');
    Exit;
  end;

  InputFile := ParamStr(1);
  OutputFile := ParamStr(2);

  // Validate shiftValue
  if not TryStrToInt(ParamStr(3), ShiftValue) or (ShiftValue < -7) or (ShiftValue > 7) then
  begin
    Writeln('Shift value must be an integer between -7 and 7.');
    Exit;
  end;
  if ShiftValue = 0 then
  begin
    Writeln('Nothing to do.');
    Exit;
  end;

  try
    ShiftBitstream(InputFile, OutputFile, ShiftValue);
  except
    on E: Exception do
      Writeln(Format('An error occurred: %s', [E.Message]));
  end;
end.

