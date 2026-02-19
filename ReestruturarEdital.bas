
Attribute VB_Name = "modReestruturarEdital"
Option Explicit

Public Sub ReestruturarEdital()
    Dim reNum As Object, reTop As Object
    Dim p As Paragraph, t As String
    Dim depth As Long

    Application.ScreenUpdating = False
    Application.StatusBar = "Reestruturando títulos e gerando sumário. Aguarde..."

    Set reNum = CreateObject("VBScript.Regexp")
    With reNum
        .Pattern = "^\s*(\n?\r?\d+(?:\.\d+){0,5})[\.)-]?\s+"
        .Global = False
        .IgnoreCase = True
    End With

    Set reTop = CreateObject("VBScript.Regexp")
    With reTop
        .Pattern = "^\s*(ANEXOS?|EDITAL|AVISO)\b"
        .Global = False
        .IgnoreCase = True
    End With

    Dim rngStory As Range
    Set rngStory = ActiveDocument.StoryRanges(wdMainTextStory)

    For Each p In rngStory.Paragraphs
        t = Trim(ClearControlChars(p.Range.Text))
        If Len(t) = 0 Then GoTo ContinueLoop

        If reNum.Test(t) Then
            depth = CountDots(GetFirstGroup(reNum, t)) + 1
            ApplyHeadingByDepth p, depth
            GoTo ContinueLoop
        End If

        If reTop.Test(t) Then
            ApplyHeadingByDepth p, 1
            GoTo ContinueLoop
        End If

        If IsAllCapsLine(t) And Len(t) <= 140 Then
            ApplyHeadingByDepth p, 1
            GoTo ContinueLoop
        End If
ContinueLoop:
    Next p

    InsertTOC_AtDocumentStart

    Application.ScreenUpdating = True
    Application.StatusBar = "Pronto!"
    MsgBox "Reestruturação concluída." & vbCrLf & _
           "Dica: clique no sumário inserido > botão direito > Atualizar campo.", vbInformation
End Sub

Private Function GetFirstGroup(ByVal re As Object, ByVal s As String) As String
    Dim m
    Set m = re.Execute(s)
    If m.Count > 0 Then
        GetFirstGroup = m(0).SubMatches(0)
    Else
        GetFirstGroup = ""
    End If
End Function

Private Function CountDots(ByVal s As String) As Long
    Dim i As Long, c As Long
    For i = 1 To Len(s)
        If Mid$(s, i, 1) = "." Then c = c + 1
    Next
    CountDots = c
End Function

Private Sub ApplyHeadingByDepth(ByVal p As Paragraph, ByVal depth As Long)
    On Error Resume Next
    Select Case True
        Case depth <= 1
            p.Range.Style = ActiveDocument.Styles(wdStyleHeading1)
        Case depth = 2
            p.Range.Style = ActiveDocument.Styles(wdStyleHeading2)
        Case Else
            p.Range.Style = ActiveDocument.Styles(wdStyleHeading3)
    End Select
End Sub

Private Function IsAllCapsLine(ByVal s As String) As Boolean
    Dim hasLetter As Boolean, i As Long, ch As String
    For i = 1 To Len(s)
        ch = Mid$(s, i, 1)
        If ch Like "[A-Za-zÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ]" Then
            hasLetter = True
            If ch <> UCase$(ch) Then
                IsAllCapsLine = False
                Exit Function
            End If
        End If
    Next
    IsAllCapsLine = hasLetter
End Function

Private Function ClearControlChars(ByVal s As String) As String
    s = Replace$(s, ChrW(13), " ")
    s = Replace$(s, ChrW(11), " ")
    s = Replace$(s, ChrW(7), " ")
    ClearControlChars = s
End Function

Private Sub InsertTOC_AtDocumentStart()
    Dim selRange As Range
    Set selRange = ActiveDocument.Range(0, 0)
    selRange.Select

    Selection.InsertParagraphBefore
    Selection.HomeKey wdStory

    Selection.TypeText "SUMÁRIO"
    On Error Resume Next
    Selection.Style = ActiveDocument.Styles(wdStyleTitle)
    On Error GoTo 0
    Selection.TypeParagraph

    ActiveDocument.TablesOfContents.Add _
        Range:=Selection.Range, _
        UseHeadingStyles:=True, _
        UpperHeadingLevel:=1, _
        LowerHeadingLevel:=3, _
        UseHyperlinks:=True, _
        HidePageNumbersInWeb:=True, _
        RightAlignPageNumbers:=True

    Selection.MoveDown Unit:=wdParagraph, Count:=1
    Selection.InsertBreak wdPageBreak
End Sub
