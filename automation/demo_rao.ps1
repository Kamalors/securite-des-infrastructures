#Requires -Version 5.1
<#
Démonstration RAO : fenêtre de pilotage de la maquette EVE-NG pendant la soutenance.
Lancer : double-clic sur automation\Demo_RAO.cmd
     ou : powershell -STA -ExecutionPolicy Bypass -File automation\demo_rao.ps1
Accès (aucun mot de passe, aucun secret dans ce fichier) :
  - clé d'administration ~/.ssh/id_ed25519_par861454 : toutes les fonctions, mêmes accès que automation/ssh_config ;
  - clé de camarade ~/.ssh/id_ed25519_rao (créée par connexion_rao.ps1) : ouverture d'EVE-NG seulement.
#>
Add-Type -AssemblyName PresentationFramework, PresentationCore, WindowsBase

$Root = Split-Path -Parent $PSScriptRoot
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
$env:PYTHONIOENCODING = 'utf-8'

$Hote = '163.172.105.87'
$PortEve = 8443
$Mode = 'aucun'
if (Test-Path "$HOME\.ssh\id_ed25519_rao") { $Mode = 'camarade' }
if (Test-Path "$HOME\.ssh\id_ed25519_par861454") { $Mode = 'admin' }

if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    [Windows.MessageBox]::Show("Le client OpenSSH est absent.`nParamètres > Système > Fonctionnalités facultatives > ajouter « Client OpenSSH ».", 'Démonstration RAO') | Out-Null
    exit 1
}

# ------------------------------------------------------------------ fenêtre
$xaml = @'
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Maquette RAO, démonstration en direct" Width="1480" Height="900" MinWidth="1150" MinHeight="720"
        WindowStartupLocation="CenterScreen" Background="#F4F1EA" Foreground="#101B2C"
        FontFamily="Segoe UI Variable Text, Segoe UI" FontSize="15" UseLayoutRounding="True">
  <Window.Resources>
    <Style x:Key="Action" TargetType="Button">
      <Setter Property="Background" Value="#FBF9F4"/>
      <Setter Property="Foreground" Value="#101B2C"/>
      <Setter Property="BorderBrush" Value="#C9C2B4"/>
      <Setter Property="Padding" Value="18,9"/>
      <Setter Property="Margin" Value="10,0,0,0"/>
      <Setter Property="FontWeight" Value="SemiBold"/>
      <Setter Property="Cursor" Value="Hand"/>
      <Setter Property="FocusVisualStyle" Value="{x:Null}"/>
      <Setter Property="Template">
        <Setter.Value>
          <ControlTemplate TargetType="Button">
            <Border x:Name="b" Background="{TemplateBinding Background}" BorderBrush="{TemplateBinding BorderBrush}"
                    BorderThickness="1.5" CornerRadius="7" Padding="{TemplateBinding Padding}">
              <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center"/>
            </Border>
            <ControlTemplate.Triggers>
              <Trigger Property="IsMouseOver" Value="True"><Setter TargetName="b" Property="Opacity" Value="0.86"/></Trigger>
              <Trigger Property="IsKeyboardFocused" Value="True"><Setter TargetName="b" Property="BorderBrush" Value="#1F7A8C"/></Trigger>
              <Trigger Property="IsEnabled" Value="False"><Setter TargetName="b" Property="Opacity" Value="0.4"/></Trigger>
            </ControlTemplate.Triggers>
          </ControlTemplate>
        </Setter.Value>
      </Setter>
    </Style>
    <Style x:Key="Primary" TargetType="Button" BasedOn="{StaticResource Action}">
      <Setter Property="Background" Value="#101B2C"/>
      <Setter Property="Foreground" Value="#F4F1EA"/>
      <Setter Property="BorderBrush" Value="#101B2C"/>
    </Style>
    <Style x:Key="Ghost" TargetType="Button" BasedOn="{StaticResource Action}">
      <Setter Property="Background" Value="Transparent"/>
      <Setter Property="Foreground" Value="#A9B4C4"/>
      <Setter Property="BorderBrush" Value="#2E3D55"/>
      <Setter Property="Padding" Value="12,4"/>
      <Setter Property="FontSize" Value="13"/>
      <Setter Property="FontWeight" Value="Normal"/>
    </Style>
    <Style x:Key="Pill" TargetType="Button">
      <Setter Property="Foreground" Value="#101B2C"/>
      <Setter Property="Cursor" Value="Hand"/>
      <Setter Property="FocusVisualStyle" Value="{x:Null}"/>
      <Setter Property="Template">
        <Setter.Value>
          <ControlTemplate TargetType="Button">
            <Border x:Name="b" Background="#FBF9F4" BorderBrush="#E1DBCF" BorderThickness="1" CornerRadius="16" Padding="12,7">
              <ContentPresenter VerticalAlignment="Center"/>
            </Border>
            <ControlTemplate.Triggers>
              <Trigger Property="IsMouseOver" Value="True"><Setter TargetName="b" Property="BorderBrush" Value="#9CC3CB"/></Trigger>
              <Trigger Property="IsKeyboardFocused" Value="True"><Setter TargetName="b" Property="BorderBrush" Value="#1F7A8C"/></Trigger>
            </ControlTemplate.Triggers>
          </ControlTemplate>
        </Setter.Value>
      </Setter>
    </Style>
    <Style x:Key="Step" TargetType="Button">
      <Setter Property="Background" Value="Transparent"/>
      <Setter Property="Foreground" Value="#101B2C"/>
      <Setter Property="HorizontalContentAlignment" Value="Stretch"/>
      <Setter Property="Margin" Value="0,2"/>
      <Setter Property="Cursor" Value="Hand"/>
      <Setter Property="FocusVisualStyle" Value="{x:Null}"/>
      <Setter Property="Template">
        <Setter.Value>
          <ControlTemplate TargetType="Button">
            <Border x:Name="b" Background="{TemplateBinding Background}" CornerRadius="8" Padding="14,8"
                    BorderThickness="2" BorderBrush="Transparent">
              <ContentPresenter HorizontalAlignment="Stretch"/>
            </Border>
            <ControlTemplate.Triggers>
              <Trigger Property="IsMouseOver" Value="True"><Setter TargetName="b" Property="Background" Value="#EFEBE2"/></Trigger>
              <Trigger Property="IsKeyboardFocused" Value="True"><Setter TargetName="b" Property="BorderBrush" Value="#1F7A8C"/></Trigger>
              <Trigger Property="IsEnabled" Value="False"><Setter TargetName="b" Property="Opacity" Value="0.45"/></Trigger>
            </ControlTemplate.Triggers>
          </ControlTemplate>
        </Setter.Value>
      </Setter>
    </Style>
  </Window.Resources>

  <Grid Margin="28,20,28,24">
    <Grid.RowDefinitions>
      <RowDefinition Height="Auto"/>
      <RowDefinition Height="*"/>
    </Grid.RowDefinitions>

    <Grid Margin="0,0,0,18">
      <Grid.ColumnDefinitions>
        <ColumnDefinition Width="*"/>
        <ColumnDefinition Width="Auto"/>
      </Grid.ColumnDefinitions>
      <StackPanel>
        <TextBlock Text="Maquette RAO" FontFamily="Segoe UI Variable Display, Segoe UI" FontSize="30" FontWeight="SemiBold"/>
        <TextBlock Text="L'architecture de l'offre, testée en direct sur le serveur Proxmox du projet" Foreground="#5A6372"/>
      </StackPanel>
      <StackPanel Grid.Column="1" Orientation="Horizontal" VerticalAlignment="Center">
        <Button x:Name="BtnServer" Style="{StaticResource Pill}" ToolTipService.ShowOnDisabled="True">
          <StackPanel Orientation="Horizontal">
            <Ellipse x:Name="DotServer" Width="10" Height="10" Fill="#C9C2B4" VerticalAlignment="Center"/>
            <TextBlock x:Name="TxtServer" Text="Serveur non vérifié" Margin="8,0,0,0" FontSize="14"/>
          </StackPanel>
        </Button>
        <Button x:Name="BtnCheck" Style="{StaticResource Action}" Content="Vérifier la maquette" Margin="22,0,0,0"/>
        <Button x:Name="BtnPve" Style="{StaticResource Action}" ToolTipService.ShowOnDisabled="True">
          <StackPanel Orientation="Horizontal">
            <Ellipse x:Name="DotPve" Width="9" Height="9" Fill="#C9C2B4" VerticalAlignment="Center"/>
            <TextBlock x:Name="TxtPve" Text="Ouvrir Proxmox" Margin="8,0,0,0"/>
          </StackPanel>
        </Button>
        <Button x:Name="BtnEve" Style="{StaticResource Primary}" ToolTipService.ShowOnDisabled="True">
          <StackPanel Orientation="Horizontal">
            <Ellipse x:Name="DotEve" Width="9" Height="9" Fill="#5A6372" VerticalAlignment="Center"/>
            <TextBlock x:Name="TxtEve" Text="Ouvrir EVE-NG" Margin="8,0,0,0"/>
          </StackPanel>
        </Button>
      </StackPanel>
    </Grid>

    <Grid Grid.Row="1">
      <Grid.ColumnDefinitions>
        <ColumnDefinition Width="350"/>
        <ColumnDefinition Width="22"/>
        <ColumnDefinition Width="*"/>
      </Grid.ColumnDefinitions>

      <Border Background="#FBF9F4" BorderBrush="#E1DBCF" BorderThickness="1" CornerRadius="10">
        <DockPanel>
          <TextBlock DockPanel.Dock="Top" Text="Scénario" FontSize="18" FontWeight="SemiBold" Margin="22,18,20,2"/>
          <TextBlock DockPanel.Dock="Top" Text="Une étape par clic, ou touches 1 à 7." Foreground="#5A6372"
                     FontSize="13.5" TextWrapping="Wrap" Margin="22,0,20,6"/>
          <Border DockPanel.Dock="Bottom" x:Name="ModeBox" Margin="14,8,14,14" Padding="14,11" CornerRadius="8" Background="#E9F1F1">
            <TextBlock x:Name="TxtMode" TextWrapping="Wrap" FontSize="13.5" Foreground="#3A4456"/>
          </Border>
          <CheckBox DockPanel.Dock="Bottom" x:Name="ChkBascule" Margin="24,4,16,0" FontSize="13.5" Foreground="#3A4456"
                    Content="Inclure la panne d'opérateur dans la recette"/>
          <ScrollViewer VerticalScrollBarVisibility="Auto" Focusable="False">
            <StackPanel x:Name="Steps" Margin="8,0,8,0"/>
          </ScrollViewer>
        </DockPanel>
      </Border>

      <Grid Grid.Column="2">
        <Grid.RowDefinitions>
          <RowDefinition Height="Auto"/>
          <RowDefinition Height="Auto"/>
          <RowDefinition Height="*"/>
        </Grid.RowDefinitions>
        <Border Background="#FBF9F4" BorderBrush="#E1DBCF" BorderThickness="1" CornerRadius="10" Padding="14,12">
          <Viewbox Stretch="Uniform" MaxHeight="300">
            <Canvas x:Name="Map" Width="1130" Height="340"/>
          </Viewbox>
        </Border>
        <Border Grid.Row="1" Margin="0,16" Background="#FBF9F4" BorderBrush="#E1DBCF" BorderThickness="1" CornerRadius="10">
          <Grid>
            <Grid.ColumnDefinitions>
              <ColumnDefinition Width="7"/>
              <ColumnDefinition Width="*"/>
              <ColumnDefinition Width="Auto"/>
            </Grid.ColumnDefinitions>
            <Border x:Name="VerdictStrip" Background="#C9C2B4" CornerRadius="10,0,0,10"/>
            <StackPanel Grid.Column="1" Margin="22,14,16,16">
              <TextBlock x:Name="VerdictTitle" FontFamily="Segoe UI Variable Display, Segoe UI" FontSize="32"
                         FontWeight="SemiBold" TextWrapping="Wrap"/>
              <TextBlock x:Name="VerdictDetail" FontSize="17" Foreground="#3A4456" TextWrapping="Wrap" Margin="0,4,0,0"/>
            </StackPanel>
            <StackPanel Grid.Column="2" Orientation="Horizontal" VerticalAlignment="Center" Margin="0,0,22,0">
              <Border x:Name="Badge" Visibility="Collapsed" VerticalAlignment="Center" CornerRadius="15" Padding="16,6">
                <TextBlock x:Name="BadgeText" FontWeight="SemiBold"/>
              </Border>
              <Button x:Name="BtnRepair" Style="{StaticResource Primary}" Content="Réparer la maquette" Visibility="Collapsed"/>
            </StackPanel>
            <ProgressBar x:Name="Busy" Grid.ColumnSpan="3" Height="3" VerticalAlignment="Bottom" Margin="10,0,10,1"
                         IsIndeterminate="True" Foreground="#1F7A8C" Background="Transparent" BorderThickness="0" Visibility="Hidden"/>
          </Grid>
        </Border>
        <Border Grid.Row="2" Background="#101B2C" CornerRadius="10">
          <DockPanel>
            <Grid DockPanel.Dock="Top" Margin="18,10,12,2">
              <TextBlock Text="Sortie brute des commandes, la preuve" Foreground="#8C99AD" FontSize="13.5" VerticalAlignment="Center"/>
              <StackPanel Orientation="Horizontal" HorizontalAlignment="Right">
                <Button x:Name="BtnCopy" Style="{StaticResource Ghost}" Content="Copier"/>
                <Button x:Name="BtnClear" Style="{StaticResource Ghost}" Content="Effacer"/>
              </StackPanel>
            </Grid>
            <RichTextBox x:Name="Term" Background="Transparent" BorderThickness="0" IsReadOnly="True" Foreground="#E6E2DA"
                         FontFamily="Cascadia Mono, Consolas" FontSize="14" Padding="12,2,12,12"
                         VerticalScrollBarVisibility="Auto" IsDocumentEnabled="False">
              <FlowDocument PagePadding="0"/>
            </RichTextBox>
          </DockPanel>
        </Border>
      </Grid>
    </Grid>
  </Grid>
</Window>
'@
$win = [Windows.Markup.XamlReader]::Parse($xaml)
foreach ($n in 'DotServer', 'TxtServer', 'DotEve', 'TxtEve', 'BtnCheck', 'BtnEve', 'BtnServer', 'BtnPve', 'DotPve', 'TxtPve',
               'TxtMode', 'ModeBox', 'ChkBascule',
               'Steps', 'Map', 'VerdictStrip', 'VerdictTitle', 'VerdictDetail', 'Badge', 'BadgeText', 'Busy', 'Term',
               'BtnCopy', 'BtnClear', 'BtnRepair') {
    Set-Variable -Name $n -Value $win.FindName($n)
}

function Brush([string]$hex) {
    $b = [Windows.Media.SolidColorBrush]::new([Windows.Media.ColorConverter]::ConvertFromString($hex)); $b.Freeze(); $b
}
$B = @{}
@{ Ink = '#101B2C'; Ink2 = '#3A4456'; Muted = '#C9C2B4'; Rule = '#D9D3C7'; Panel = '#FBF9F4'; Op = '#EBE7DE'
   Teal = '#1F7A8C'; TealL = '#7FC8D6'; TealBg = '#D6E8EA'; Orange = '#CC6226'; OrangeBg = '#F7E2D2'; Paper = '#F4F1EA'
   Actif = '#FFFFFF'; Chip = '#B9D7DC'; TermTxt = '#E6E2DA'; TermFort = '#FFFFFF'; TermCmd = '#7FC8D6'
   TermOk = '#8FD3C1'; TermKo = '#EFA272'; TermInfo = '#A9B4C4' }.GetEnumerator() | ForEach-Object { $B[$_.Key] = Brush $_.Value }

# ------------------------------------------------------------------ schéma de la maquette
$Noeuds = [ordered]@{
    web = @{ X = 16;  Y = 18;  W = 150; H = 38; Nom = 'Web';             Hote = 'srv-web'; Type = 'chip' }
    app = @{ X = 16;  Y = 68;  W = 150; H = 38; Nom = 'Application';     Hote = 'srv-app'; Type = 'chip' }
    db  = @{ X = 16;  Y = 118; W = 150; H = 38; Nom = 'Base de données'; Hote = 'srv-db';  Type = 'chip' }
    bas = @{ X = 16;  Y = 168; W = 150; H = 38; Nom = 'Bastion';         Hote = 'bastion'; Type = 'chip' }
    log = @{ X = 16;  Y = 218; W = 150; H = 38; Nom = 'Journaux';        Hote = 'logs';    Type = 'chip' }
    dc1 = @{ X = 250; Y = 84;  W = 210; H = 62; Nom = 'Datacenter 1';    Hote = 'fw-dc1';  Type = 'dc' }
    dc2 = @{ X = 250; Y = 262; W = 210; H = 62; Nom = 'Datacenter 2';    Hote = 'fw-dc2';  Type = 'dc' }
    opa = @{ X = 610; Y = 74;  W = 88;  H = 88; Nom = 'Opérateur A';     Hote = 'isp-a';   Type = 'op' }
    opb = @{ X = 610; Y = 250; W = 88;  H = 88; Nom = 'Opérateur B';     Hote = 'isp-b';   Type = 'op' }
    hq  = @{ X = 880; Y = 22;  W = 230; H = 62; Nom = 'Siège';           Hote = 'gw-hq';   Type = 'site' }
    ag  = @{ X = 880; Y = 146; W = 230; H = 62; Nom = 'Agence France';   Hote = 'gw-agfr'; Type = 'site' }
    pa  = @{ X = 880; Y = 270; W = 230; H = 62; Nom = 'Partenaire';      Hote = 'gw-part'; Type = 'site' }
}
# dernier octet de l'adresse de gestion (10.98.0.x) -> nœud du schéma
$Adresses = @{ 11 = 'opa'; 12 = 'opb'; 13 = 'dc1'; 14 = 'dc2'; 15 = 'hq'; 16 = 'ag'; 17 = 'pa'
               101 = 'web'; 102 = 'app'; 103 = 'db'; 104 = 'bas'; 105 = 'log'; 106 = 'cli-ag'; 107 = 'cli-ext'; 108 = 'cli-inv' }

function Centre($k) { $n = $Noeuds[$k]; @(($n.X + $n.W / 2), ($n.Y + $n.H / 2)) }
function New-Line($de, $vers, $brush, [double]$w) {
    $p, $q = (Centre $de), (Centre $vers)
    $l = New-Object Windows.Shapes.Line
    $l.X1, $l.Y1, $l.X2, $l.Y2 = $p[0], $p[1], $q[0], $q[1]
    $l.Stroke = $brush; $l.StrokeThickness = $w
    [void]$Map.Children.Add($l); $l
}

$Liens = [ordered]@{}
foreach ($pair in @('web', 'dc1'), @('app', 'dc1'), @('db', 'dc1'), @('bas', 'dc1'), @('log', 'dc1'), @('dc1', 'opa'),
                  @('dc1', 'opb'), @('dc2', 'opa'), @('dc2', 'opb'), @('hq', 'opa'), @('hq', 'opb'), @('ag', 'opa'),
                  @('ag', 'opb'), @('pa', 'opa')) {
    $Liens["$($pair[0])-$($pair[1])"] = New-Line $pair[0] $pair[1] $B.Rule 2
}
$Tunnels = foreach ($k in 'hq', 'ag', 'pa', 'dc2') {
    $t = New-Line 'dc1' $k $B.Teal 2.5
    $t.StrokeDashArray = [Windows.Media.DoubleCollection]::Parse('5 3'); $t.Visibility = 'Collapsed'; $t
}

$Boites = @{}
$Points = @{}
foreach ($k in $Noeuds.Keys) {
    $n = $Noeuds[$k]
    $bd = New-Object Windows.Controls.Border
    $bd.Width, $bd.Height, $bd.Tag = $n.W, $n.H, $n.Hote
    $bd.BorderThickness = [Windows.Thickness]::new(1.5)
    $fg = $B.Ink
    switch ($n.Type) {
        'dc'   { $bd.Background = $B.Ink; $bd.BorderBrush = $B.Ink; $bd.CornerRadius = [Windows.CornerRadius]::new(8); $fg = $B.Paper }
        'site' { $bd.Background = $B.Panel; $bd.BorderBrush = $B.Ink; $bd.CornerRadius = [Windows.CornerRadius]::new(8) }
        'op'   { $bd.Background = $B.Op; $bd.BorderBrush = $B.Ink2; $bd.CornerRadius = [Windows.CornerRadius]::new($n.W / 2) }
        'chip' { $bd.Background = $B.Panel; $bd.BorderBrush = $B.Chip; $bd.CornerRadius = [Windows.CornerRadius]::new(6) }
    }
    $sp = New-Object Windows.Controls.StackPanel
    $sp.VerticalAlignment = 'Center'; $sp.HorizontalAlignment = 'Center'
    $t1 = New-Object Windows.Controls.TextBlock
    $t1.Text = if ($n.Type -eq 'op') { $n.Nom -replace 'Opérateur ', 'Op. ' } else { $n.Nom }
    $t1.FontSize = if ($n.Type -eq 'chip') { 13.5 } else { 16 }
    $t1.FontWeight = 'SemiBold'; $t1.Foreground = $fg; $t1.HorizontalAlignment = 'Center'
    [void]$sp.Children.Add($t1)
    if ($n.Type -ne 'chip') {
        $t2 = New-Object Windows.Controls.TextBlock
        $t2.Text = $n.Hote; $t2.FontFamily = 'Cascadia Mono, Consolas'; $t2.FontSize = 12; $t2.HorizontalAlignment = 'Center'
        $t2.Foreground = if ($n.Type -eq 'dc') { $B.TealL } else { $B.Ink2 }
        [void]$sp.Children.Add($t2)
    }
    $bd.Child = $sp
    $bd.ToolTip = if ($Mode -eq 'admin') { "Ouvrir une console sur $($n.Hote)" } else { $n.Hote }
    if ($Mode -eq 'admin') {
        $bd.Cursor = 'Hand'
        $bd.Add_MouseLeftButtonUp({ param($s, $e) Open-Console $s.Tag })
    }
    [Windows.Controls.Canvas]::SetLeft($bd, $n.X); [Windows.Controls.Canvas]::SetTop($bd, $n.Y)
    [void]$Map.Children.Add($bd)
    $Boites[$k] = @{ Border = $bd; Defaut = $bd.BorderBrush }

    $dot = New-Object Windows.Shapes.Ellipse
    $dot.Width = $dot.Height = 10; $dot.Fill = $B.Muted; $dot.Stroke = $B.Panel; $dot.StrokeThickness = 1.5
    $dx = if ($n.Type -eq 'op') { $n.W - 18 } else { $n.W - 16 }
    [Windows.Controls.Canvas]::SetLeft($dot, $n.X + $dx); [Windows.Controls.Canvas]::SetTop($dot, $n.Y + 6)
    [void]$Map.Children.Add($dot)
    $Points[$k] = $dot
}

# croix posée sur le lien base de données - datacenter lors du refus
$Croix = New-Object Windows.Shapes.Path
$Croix.Data = [Windows.Media.Geometry]::Parse('M0,0 L16,16 M16,0 L0,16')
$Croix.Stroke = $B.Orange; $Croix.StrokeThickness = 3.5; $Croix.Visibility = 'Collapsed'
$m = @((((Centre 'db')[0] + (Centre 'dc1')[0]) / 2), (((Centre 'db')[1] + (Centre 'dc1')[1]) / 2))
[Windows.Controls.Canvas]::SetLeft($Croix, $m[0] - 8); [Windows.Controls.Canvas]::SetTop($Croix, $m[1] - 8)
[void]$Map.Children.Add($Croix)

function Reset-Map {
    foreach ($l in $Liens.Values) {
        $l.Stroke = $B.Rule; $l.StrokeThickness = 2; $l.ClearValue([Windows.Shapes.Shape]::StrokeDashArrayProperty)
    }
    foreach ($t in $Tunnels) { $t.Visibility = 'Collapsed' }
    foreach ($bx in $Boites.Values) { $bx.Border.BorderBrush = $bx.Defaut; $bx.Border.BorderThickness = [Windows.Thickness]::new(1.5) }
    $Croix.Visibility = 'Collapsed'
}
function Paint([string[]]$cles, $brush, [double]$w = 4, [switch]$Dash) {
    foreach ($k in $cles) {
        $l = $Liens[$k]; $l.Stroke = $brush; $l.StrokeThickness = $w
        if ($Dash) { $l.StrokeDashArray = [Windows.Media.DoubleCollection]::Parse('3 2') }
    }
}
function Glow([string]$k, $brush) { $Boites[$k].Border.BorderBrush = $brush; $Boites[$k].Border.BorderThickness = [Windows.Thickness]::new(3) }

function Show-Map([int]$etape) {
    Reset-Map
    switch ($etape) {
        1 { foreach ($t in $Tunnels) { $t.Visibility = 'Visible' }; Glow 'dc1' $B.TealL }
        2 { Paint 'dc1-opa', 'hq-opa', 'ag-opa', 'pa-opa' $B.Teal 3.5; Paint 'dc1-opb', 'hq-opb', 'ag-opb' $B.Teal 2 -Dash }
        3 { Paint 'pa-opa', 'dc1-opa', 'app-dc1' $B.Teal; Glow 'pa' $B.Teal; Glow 'app' $B.Teal }
        4 { Paint 'pa-opa', 'dc1-opa' $B.Orange; Paint 'db-dc1' $B.Orange 3 -Dash; Glow 'pa' $B.Orange; Glow 'db' $B.Orange
            $Croix.Visibility = 'Visible' }
        5 { Paint 'log-dc1' $B.Teal; Glow 'dc1' $B.TealL; Glow 'log' $B.Teal }
        6 { Paint 'ag-opa', 'dc1-opa' $B.Teal; Glow 'ag' $B.Teal }
        7 { Paint @($Liens.Keys) $B.Teal 2.5 }
    }
}
# phases de la panne d'opérateur, signalées par le travail en arrière-plan
function Show-Phase([string]$phase) {
    if ($phase -eq 'coupure') {
        Reset-Map; Paint 'ag-opa' $B.Orange 3 -Dash; Paint 'ag-opb', 'dc1-opb' $B.Teal; Glow 'ag' $B.Orange
    } elseif ($phase -eq 'retour') { Show-Map 6 }
}

# ------------------------------------------------------------------ affichage
$MotifKo = 'échoué|NON CONFORME|Permission denied|Could not resolve|Connection refused|Connection timed out|No route|erreur'
$MotifOk = 'réussi|CONFORME|ESTABLISHED|\bFull\b|succeeded|\bopen\b|RAO-OK|^up |Preuves'
$MotifRefus = 'RAO-REFUS|timed out|^down '

function Add-Line([string]$ton, [string]$texte) {
    $p = New-Object Windows.Documents.Paragraph
    $p.Margin = [Windows.Thickness]::new(0)
    switch ($ton) {
        'cmd' {
            $p.Margin = [Windows.Thickness]::new(0, 10, 0, 2)
            $r1 = New-Object Windows.Documents.Run('$ '); $r1.Foreground = $B.TermCmd; $p.Inlines.Add($r1)
            $r2 = New-Object Windows.Documents.Run($texte); $r2.Foreground = $B.TermFort; $p.Inlines.Add($r2)
        }
        'info' {
            $p.Margin = [Windows.Thickness]::new(0, 8, 0, 0)
            $r = New-Object Windows.Documents.Run($texte); $r.Foreground = $B.TermInfo; $r.FontStyle = 'Italic'; $p.Inlines.Add($r)
        }
        default {
            $r = New-Object Windows.Documents.Run($texte)
            $r.Foreground = $B.TermTxt
            if ($texte -match $MotifKo) { $r.Foreground = $B.TermKo }
            elseif ($texte -match $MotifOk) { $r.Foreground = $B.TermOk }
            elseif ($texte -match $MotifRefus) { $r.Foreground = $B.TermKo }
            $p.Inlines.Add($r)
        }
    }
    $Term.Document.Blocks.Add($p)
    while ($Term.Document.Blocks.Count -gt 800) { [void]$Term.Document.Blocks.Remove($Term.Document.Blocks.FirstBlock) }
    $Term.ScrollToEnd()
}

function Set-Verdict([string]$titre, [string]$detail, [string]$ton = 'idle', [string]$etiquette = '', [switch]$Reparer) {
    $VerdictTitle.Text = $titre; $VerdictDetail.Text = $detail
    $VerdictStrip.Background = switch ($ton) { 'ok' { $B.Teal } 'refus' { $B.Orange } 'ko' { $B.Orange } 'busy' { $B.Ink } default { $B.Muted } }
    if ($etiquette) {
        $Badge.Visibility = 'Visible'; $BadgeText.Text = $etiquette
        if ($ton -eq 'ko') { $Badge.Background = $B.OrangeBg; $BadgeText.Foreground = $B.Orange }
        else { $Badge.Background = $B.TealBg; $BadgeText.Foreground = $B.Teal }
    } else { $Badge.Visibility = 'Collapsed' }
    $BtnRepair.Visibility = if ($Reparer -and $Mode -eq 'admin') { 'Visible' } else { 'Collapsed' }
}
function Set-Pill($dot, $txt, [string]$etat, [string]$texte) {
    $dot.Fill = switch ($etat) { 'ok' { $B.Teal } 'ko' { $B.Orange } default { $B.Muted } }
    $txt.Text = $texte
}

$StepButtons = @{}
function Set-StepState([int]$n, [string]$etat) {
    $num = $StepButtons[$n].Content.Children[0]
    $fond = switch ($etat) { 'ok' { $B.Teal } 'ko' { $B.Orange } default { $null } }
    $num.Background = $fond
    $num.BorderBrush = if ($fond) { $fond } else { $B.Ink }
    $num.Child.Foreground = if ($fond) { $B.Paper } else { $B.Ink }
}
function Set-Active([int]$n) {
    foreach ($k in $StepButtons.Keys) { $StepButtons[$k].Background = if ($k -eq $n) { $B.Actif } else { [Windows.Media.Brushes]::Transparent } }
}
function Set-BusyState([bool]$occupe) {
    $Busy.Visibility = if ($occupe) { 'Visible' } else { 'Hidden' }
    $actif = (-not $occupe) -and ($Mode -eq 'admin')
    foreach ($sb in $StepButtons.Values) { $sb.IsEnabled = $actif }
    $BtnCheck.IsEnabled = $actif
    $BtnRepair.IsEnabled = $actif
}

# ------------------------------------------------------------------ travail en arrière-plan (la fenêtre reste fluide)
$sync = [hashtable]::Synchronized(@{ Queue = New-Object 'System.Collections.Concurrent.ConcurrentQueue[object]'; Phase = ''; SshErr = @('', '') })
$Common = {
    Set-Location -LiteralPath $Root
    [Environment]::CurrentDirectory = $Root
    function Say([string]$t, [string]$ton = 'out') { $sync.Queue.Enqueue(@($ton, $t)) }
    function Node([string]$h, [string]$cmd) {
        Say "[$h] $cmd" 'cmd'
        $lignes = New-Object System.Collections.Generic.List[string]
        & ssh -n -F automation/ssh_config -o ConnectTimeout=8 $h $cmd 2>&1 | ForEach-Object { $l = "$_"; $lignes.Add($l); Say $l }
        $code = $LASTEXITCODE
        if ($code -eq 255) { $sync.SshErr = @($h, ($lignes -join ' ')) }
        @{ Code = $code; Text = ($lignes -join "`n"); Lines = $lignes }
    }
}
$script:Job = $null
$CmdSante = 'echo sante disque=$(df --output=pcent / | tail -1 | tr -dc 0-9) ospf=$(vtysh -c ''show ip ospf neighbor'' 2>/dev/null | grep -c Full) tunnels=$(swanctl --list-sas 2>/dev/null | grep -c ESTABLISHED) frr=$(systemctl is-active frr)'
function Start-Action([string]$libelle, [scriptblock]$travail, [scriptblock]$fin, [hashtable]$vars = @{}) {
    if ($script:Job) { return }
    Set-BusyState $true
    Set-Verdict "$libelle…" 'Commande en cours sur la maquette.' 'busy'
    $rs = [runspacefactory]::CreateRunspace(); $rs.Open()
    $rs.SessionStateProxy.SetVariable('sync', $sync); $rs.SessionStateProxy.SetVariable('Root', $Root)
    foreach ($k in $vars.Keys) { $rs.SessionStateProxy.SetVariable($k, $vars[$k]) }
    $ps = [powershell]::Create(); $ps.Runspace = $rs
    [void]$ps.AddScript($Common.ToString() + "`n" + $travail.ToString())
    $script:Job = @{ PS = $ps; Handle = $ps.BeginInvoke(); Fin = $fin }
}
function Test-SshKo($r, [int]$n) {
    if (-not $r.SshKo) { return $false }
    $h, $msg = $sync.SshErr
    if ($msg -match 'No route to host|stdio forwarding failed|Connection timed out during banner') {
        # le serveur répond, mais la machine visée est éteinte
        Set-Verdict "La machine $h est éteinte" 'Ouvrez EVE-NG, sélectionnez tous les nœuds, clic droit, Start. Attendez une minute, puis cliquez sur « Vérifier la maquette ».' 'ko' 'À vérifier'
    } else {
        Set-Pill $DotServer $TxtServer 'ko' 'Serveur injoignable'
        Set-Verdict 'La maquette ne répond pas' 'La connexion SSH au serveur a échoué. Vérifiez la connexion Internet, puis cliquez sur « Vérifier la maquette ».' 'ko' 'À vérifier'
    }
    if ($n) { Set-StepState $n 'ko' }
    $true
}

# ------------------------------------------------------------------ étapes du scénario
function Start-Check {
    Reset-Map
    foreach ($d in $Points.Values) { $d.Fill = $B.Muted }
    Start-Action 'Vérification de la maquette' {
        $h = Node 'par861454' 'echo serveur-ok'
        if ($h.Text -notmatch 'serveur-ok') { return @{ Serveur = $false } }
        $e = Node 'eve' 'for i in 11 12 13 14 15 16 17 101 102 103 104 105 106 107 108; do if ping -c1 -W1 10.98.0.$i >/dev/null 2>&1; then echo up $i; else echo down $i; fi; done'
        $sante = if ($e.Text -match 'up 13\b') { (Node 'fw-dc1' $CmdSante).Text } else { '' }
        @{ Serveur = $true; Eve = ($e.Text -match '(up|down) \d'); Lignes = $e.Lines; Sante = $sante }
    } {
        param($r)
        if (-not $r.Serveur) {
            Set-Pill $DotServer $TxtServer 'ko' 'Serveur injoignable'
            Set-Verdict 'Le serveur Proxmox ne répond pas' 'Vérifiez la connexion Internet et la clé ~/.ssh/id_ed25519_par861454.' 'ko' 'À vérifier'
            return
        }
        Set-Pill $DotServer $TxtServer 'ok' 'Serveur joignable'
        if (-not $r.Eve) {
            Set-Verdict 'La machine EVE-NG ne répond pas' 'En root sur le serveur : qm start 200, puis démarrer les nœuds dans EVE-NG.' 'ko' 'À vérifier'
            return
        }
        $hs = @()
        foreach ($l in $r.Lignes) {
            if ($l -match '^(up|down) (\d+)$') {
                $k = $Adresses[[int]$Matches[2]]
                if ($Points.ContainsKey($k)) { $Points[$k].Fill = if ($Matches[1] -eq 'up') { $B.Teal } else { $B.Orange } }
                if ($Matches[1] -eq 'down') { $hs += if ($Noeuds.Contains($k)) { $Noeuds[$k].Hote } else { $k } }
            }
        }
        $probleme = ''
        if ($r.Sante -match 'disque=(\d+) ospf=(\d+) tunnels=(\d+) frr=(\S+)') {
            $disque, $voisins, $tun, $frr = [int]$Matches[1], [int]$Matches[2], [int]$Matches[3], $Matches[4]
            if ($disque -ge 90) { $probleme = "Le disque de fw-dc1 est plein à $disque %." }
            elseif ($frr -ne 'active' -or $voisins -lt 5) { $probleme = "Le routage OSPF ne tourne pas correctement sur fw-dc1 ($voisins voisins sur 5)." }
            elseif ($tun -lt 6) { $probleme = "Seuls $tun tunnels chiffrés sur 6 sont établis." }
        }
        if (-not $hs -and -not $probleme) {
            Set-Verdict 'La maquette est prête' '15 machines sur 15 répondent, 6 tunnels chiffrés et 5 voisins de routage. La démonstration peut commencer.' 'ok' 'Prête'
        } elseif (-not $hs) {
            Set-Verdict 'Les machines répondent, mais la maquette est dégradée' "$probleme Cliquez sur « Réparer la maquette » : la configuration est relancée en une minute environ." 'ko' 'À vérifier' -Reparer
        } else {
            Set-Verdict "$(15 - $hs.Count) machines sur 15 répondent" "Hors ligne : $($hs -join ', '). Démarrez-les dans EVE-NG (tout sélectionner, clic droit, Start) ou, pour un conteneur, pct start en root sur le serveur." 'ko' 'À vérifier'
        }
    } @{ CmdSante = $CmdSante }
}

function Start-Repair {
    if ($script:Job -or $Mode -ne 'admin') { return }
    Set-Active 0
    Reset-Map
    foreach ($i in 1..7) { Set-StepState $i 'none' }
    Start-Action 'Relance de la configuration (environ une minute)' {
        $py = if (Get-Command python -ErrorAction SilentlyContinue) { 'python' } else { 'py' }
        Say "$py -u automation/lab/deploy.py" 'cmd'
        & $py -u automation/lab/deploy.py 2>&1 | ForEach-Object { Say "$_" }
        Say 'Attente de la remontée des tunnels et du routage (20 s).' 'info'
        Start-Sleep 20
        $s = Node 'fw-dc1' $CmdSante
        @{ SshKo = ($s.Code -eq 255); Sante = $s.Text }
    } {
        param($r)
        if (Test-SshKo $r 0) { return }
        if ($r.Sante -match 'ospf=(\d+) tunnels=(\d+) frr=active' -and [int]$Matches[1] -ge 5 -and [int]$Matches[2] -ge 6) {
            Set-Verdict 'La maquette est réparée' '6 tunnels chiffrés et 5 voisins de routage. Vous pouvez reprendre le scénario.' 'ok' 'Prête'
        } else {
            Set-Verdict 'La réparation n''a pas suffi' 'Lisez la sortie ci-dessous et vérifiez la place disque des routeurs (df -h).' 'ko' 'À vérifier' -Reparer
        }
    } @{ CmdSante = $CmdSante }
}

function Invoke-Step([int]$n) {
    if ($script:Job -or $Mode -ne 'admin') { return }
    if ($n -eq 6) {
        $ok = [Windows.MessageBox]::Show("Couper la ligne de l'opérateur A de l'agence pendant 10 secondes ?`nL'agence la rétablit elle-même ensuite, même si cette fenêtre se ferme.", 'Panne d''opérateur', 'OKCancel', 'Question')
        if ($ok -ne 'OK') { return }
    }
    Set-Active $n
    Show-Map $n
    switch ($n) {
        1 {
            Start-Action 'Comptage des tunnels chiffrés' {
                $r = Node 'fw-dc1' 'swanctl --list-sas 2>/dev/null | grep ESTABLISHED'
                @{ SshKo = ($r.Code -eq 255); N = @($r.Lines | Where-Object { $_ -match 'ESTABLISHED' }).Count }
            } {
                param($r)
                if (Test-SshKo $r 1) { return }
                if ($r.N -ge 6) { Set-Verdict "$($r.N) tunnels chiffrés sont établis" 'Le datacenter 1 a un tunnel IPsec ouvert vers chaque site, sur chacun de ses opérateurs.' 'ok' 'Conforme'; Set-StepState 1 'ok' }
                else { Set-Verdict "$($r.N) tunnels établis sur 6 attendus" 'Cliquez sur « Réparer la maquette » : la configuration est relancée en une minute environ.' 'ko' 'À vérifier' -Reparer; Set-StepState 1 'ko' }
            }
        }
        2 {
            Start-Action 'Lecture de la table de routage' {
                $r = Node 'fw-dc1' "vtysh -c 'show ip ospf neighbor'"
                @{ SshKo = ($r.Code -eq 255); Arret = ($r.Text -match 'not running'); N = @($r.Lines | Where-Object { $_ -match '\bFull\b' }).Count }
            } {
                param($r)
                if (Test-SshKo $r 2) { return }
                if ($r.Arret) { Set-Verdict 'Le routage OSPF est arrêté sur fw-dc1' 'Sans lui, le trafic des sites ne passe plus par les tunnels. Cliquez sur « Réparer la maquette ».' 'ko' 'À vérifier' -Reparer; Set-StepState 2 'ko'; return }
                if ($r.N -ge 5) { Set-Verdict "$($r.N) voisins de routage actifs" 'Les sites sont joints par l''opérateur A, avec l''opérateur B prêt en secours.' 'ok' 'Conforme'; Set-StepState 2 'ok' }
                else { Set-Verdict "$($r.N) voisins de routage sur 5 attendus" 'Un tunnel est peut-être tombé. Cliquez sur « Réparer la maquette ».' 'ko' 'À vérifier' -Reparer; Set-StepState 2 'ko' }
            }
        }
        3 {
            Start-Action 'Le partenaire tente d''atteindre l''application' {
                $r = Node 'gw-part' 'nc -zv -w 3 -s 10.60.1.1 10.11.20.20 8443 2>&1; echo code=$?'
                @{ SshKo = ($r.Code -eq 255); Code = $(if ($r.Text -match 'code=(\d+)') { [int]$Matches[1] } else { -1 }) }
            } {
                param($r)
                if (Test-SshKo $r 3) { return }
                if ($r.Code -eq 0) { Set-Verdict 'Autorisé, comme prévu' 'Le partenaire atteint l''application (port 8443) à travers son tunnel chiffré. L''échange est écrit dans les règles du pare-feu.' 'ok' 'Conforme'; Set-StepState 3 'ok' }
                else { Set-Verdict 'L''échange autorisé ne passe pas' 'Le tunnel du partenaire est peut-être tombé. Cliquez sur « Réparer la maquette ».' 'ko' 'À vérifier' -Reparer; Set-StepState 3 'ko' }
            }
        }
        4 {
            Start-Action 'Le partenaire tente d''atteindre la base de données' {
                $r = Node 'gw-part' 'nc -zv -w 3 -s 10.60.1.1 10.11.30.30 5432 2>&1; echo code=$?'
                @{ SshKo = ($r.Code -eq 255); Code = $(if ($r.Text -match 'code=(\d+)') { [int]$Matches[1] } else { -1 }) }
            } {
                param($r)
                if (Test-SshKo $r 4) { return }
                if ($r.Code -gt 0) { Set-Verdict 'Refusé, comme prévu' 'Le pare-feu du datacenter bloque l''accès du partenaire à la base de données (port 5432). Rien ne l''autorise : c''est le refus par défaut.' 'refus' 'Conforme'; Set-StepState 4 'ok' }
                elseif ($r.Code -eq 0) { Set-Verdict 'La base de données est joignable' 'Anomalie : le partenaire ne devrait pas l''atteindre. Cliquez sur « Réparer la maquette ».' 'ko' 'À vérifier' -Reparer; Set-StepState 4 'ko' }
                else { Set-Verdict 'Le test n''a pas pu s''exécuter' 'Relancez l''étape.' 'ko' 'À vérifier'; Set-StepState 4 'ko' }
            }
        }
        5 {
            Start-Action 'Lecture du journal du pare-feu' {
                $r = Node 'fw-dc1' 'journalctl -k --since -10min --no-pager | grep -E ''RAO-(OK|REFUS) '' | tail -n 12'
                @{ SshKo = ($r.Code -eq 255); Ok = @($r.Lines | Where-Object { $_ -match 'RAO-OK' }).Count; Refus = @($r.Lines | Where-Object { $_ -match 'RAO-REFUS ' }).Count }
            } {
                param($r)
                if (Test-SshKo $r 5) { return }
                if ($r.Ok + $r.Refus -gt 0) { Set-Verdict 'Les essais sont tracés' "Dans les 10 dernières minutes, le pare-feu a enregistré $($r.Ok) échange(s) autorisé(s) et $($r.Refus) refus, avec la source, la destination et le port." 'ok' 'Conforme'; Set-StepState 5 'ok' }
                else { Set-Verdict 'Aucune trace récente' 'Lancez d''abord les étapes 3 et 4 : chaque essai laisse une ligne dans le journal.' 'idle' }
            }
        }
        6 {
            $sync.Phase = ''
            Start-Action 'Panne de l''opérateur A à l''agence' {
                Say 'Mesure : le poste de l''agence envoie un ping toutes les 0,2 s vers l''application.' 'info'
                $null = Node 'cli-ag' 'rm -f /tmp/demo_ping.log; nohup ping -q -i 0.2 -c 120 10.11.20.20 > /tmp/demo_ping.log 2>&1 &'
                Start-Sleep 4
                $avant = Node 'gw-agfr' 'ip route get 10.11.20.20'
                if ($avant.Code -eq 255) { return @{ SshKo = $true } }
                Say 'Coupure de la ligne A pendant 10 s. L''agence la rétablit elle-même (nohup), même si la connexion se perd.' 'info'
                $null = Node 'gw-agfr' 'nohup sh -c ''ip link set eth1 down; sleep 10; ip link set eth1 up'' >/dev/null 2>&1 &'
                $sync.Phase = 'coupure'
                Start-Sleep 5
                $pendant = Node 'gw-agfr' 'ip route get 10.11.20.20'
                Start-Sleep 7
                $null = Node 'gw-agfr' 'ip link set eth1 up'
                $sync.Phase = 'retour'
                Say 'Ligne A rétablie : attente du retour automatique du routage.' 'info'
                Start-Sleep 8
                $apres = Node 'gw-agfr' 'ip route get 10.11.20.20'
                Start-Sleep 2
                $ping = Node 'cli-ag' 'for i in $(seq 1 20); do grep -q transmitted /tmp/demo_ping.log && break; sleep 1; done; tail -n 2 /tmp/demo_ping.log'
                @{ SshKo = $false; Avant = $avant.Text; Pendant = $pendant.Text; Apres = $apres.Text; Ping = $ping.Text }
            } {
                param($r)
                if (Test-SshKo $r 6) { return }
                $coupure = ''
                if ($r.Ping -match '(\d+) packets transmitted, (\d+) received') {
                    $s = ([int]$Matches[1] - [int]$Matches[2]) * 0.2
                    $coupure = $s.ToString('0.0', [Globalization.CultureInfo]::GetCultureInfo('fr-FR'))
                }
                if ($r.Pendant -match 'xb-dc1' -and $r.Apres -match 'xa-dc1') {
                    $t = if ($coupure) { "Bascule réussie : $coupure s de coupure" } else { 'Bascule réussie' }
                    Set-Verdict $t 'Pendant la panne, le trafic de l''agence est passé par l''opérateur B, puis il est revenu seul sur l''opérateur A.' 'ok' 'Conforme'
                    Set-StepState 6 'ok'
                } elseif ($r.Avant -notmatch 'dev x[ab]-dc1') {
                    Set-Verdict 'Le trafic de l''agence ne passe pas par les tunnels' 'Le routage OSPF ne fonctionne pas : la panne ne peut pas basculer d''un tunnel à l''autre. Cliquez sur « Réparer la maquette ».' 'ko' 'À vérifier' -Reparer
                    Set-StepState 6 'ko'
                } else {
                    Set-Verdict 'La bascule n''a pas eu lieu comme prévu' 'Lisez les routes ci-dessous. La ligne A a été rétablie automatiquement ; refaites l''étape dans une minute.' 'ko' 'À vérifier' -Reparer
                    Set-StepState 6 'ko'
                }
            }
        }
        7 {
            Start-Action 'Recette complète en cours (environ 1 minute)' {
                $py = if (Get-Command python -ErrorAction SilentlyContinue) { 'python' } else { 'py' }
                $pyArgs = @('-u', 'automation/lab/recette.py')
                if (-not $Bascule) { $pyArgs += '--sans-bascule' }
                Say "$py $($pyArgs -join ' ')" 'cmd'
                $lignes = New-Object System.Collections.Generic.List[string]
                & $py @pyArgs 2>&1 | ForEach-Object { $l = "$_"; $lignes.Add($l); Say $l }
                @{ SshKo = $false; Text = ($lignes -join "`n") }
            } {
                param($r)
                if ($r.Text -match 'R.SULTAT : (NON CONFORME|CONFORME)') {
                    $etat = $Matches[1]
                    $flux = if ($r.Text -match 'flux (\d+)/(\d+)') { "$($Matches[1]) tests sur $($Matches[2])" } else { '' }
                    $preuves = if ($r.Text -match 'Preuves : (\S+)') { $Matches[1] } else { 'evidence/' }
                    if ($etat -eq 'CONFORME') { Set-Verdict "Recette conforme : $flux" "Preuves horodatées et empreintes SHA-256 écrites dans $preuves" 'ok' 'Conforme'; Set-StepState 7 'ok' }
                    else { Set-Verdict "Recette non conforme : $flux" 'Le détail des échecs est dans la sortie ci-dessous. Cliquez sur « Réparer la maquette », puis relancez la recette.' 'ko' 'À vérifier' -Reparer; Set-StepState 7 'ko' }
                } else {
                    Set-Verdict 'La recette n''a pas pu démarrer' 'Python est-il installé ? Commande lancée : python automation/lab/recette.py' 'ko' 'À vérifier'; Set-StepState 7 'ko'
                }
            } @{ Bascule = [bool]$ChkBascule.IsChecked }
        }
    }
}

function Open-Console([string]$h) {
    if ($Mode -ne 'admin') { return }
    Start-Process powershell.exe -WorkingDirectory $Root -ArgumentList "-NoExit -Command `$host.UI.RawUI.WindowTitle='Console $h'; ssh -F automation/ssh_config $h"
}

# ------------------------------------------------------------------ interfaces web par tunnel SSH (EVE-NG et Proxmox)
# Équivaut à : ssh -F automation/ssh_config -N -L 8443:10.99.0.10:443 lab-host   (Proxmox : -L 8006:127.0.0.1:8006)
$Services = [ordered]@{
    eve = @{ Nom = 'EVE-NG';  Port = $PortEve; Cible = '10.99.0.10:443'; Dot = $DotEve; Txt = $TxtEve; Allume = $B.TealL; Eteint = (Brush '#5A6372')
             Aide = 'lab RAO'; Proc = $null; Depuis = $null }
    pve = @{ Nom = 'Proxmox'; Port = 8006; Cible = '127.0.0.1:8006'; Dot = $DotPve; Txt = $TxtPve; Allume = $B.Teal; Eteint = $B.Muted
             Aide = 'connectez-vous avec votre compte Proxmox'; Proc = $null; Depuis = $null }
}
function Test-PortOuvert([int]$port) {
    [bool]([Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners() | Where-Object { $_.Port -eq $port })
}
function Update-Services {
    foreach ($s in $Services.Values) {
        if (Test-PortOuvert $s.Port) { $s.Dot.Fill = $s.Allume; $s.Txt.Text = "$($s.Nom) ouvert" }
        elseif (-not $s.Depuis) { $s.Dot.Fill = $s.Eteint; $s.Txt.Text = "Ouvrir $($s.Nom)" }
    }
}
function Open-Service([string]$k) {
    $s = $Services[$k]
    if ($Mode -eq 'aucun') {
        Set-Verdict 'Aucune clé SSH sur ce PC' 'Lancez d''abord automation\connexion_rao.ps1 : il crée votre clé et la copie pour le responsable du serveur.' 'ko' 'À vérifier'
        return
    }
    if (Test-PortOuvert $s.Port) { Start-Process "https://localhost:$($s.Port)"; return }
    if ($Mode -eq 'admin') {
        $sshArgs = "-F automation/ssh_config -N -L $($s.Port):$($s.Cible) -o ExitOnForwardFailure=yes lab-host"
    } else {
        $kh = "$HOME\.ssh\known_hosts_rao"
        # clé publique de l'hôte épinglée (même ligne que connexion_rao.ps1) : refuse un serveur usurpé
        if (-not (Test-Path $kh)) { Set-Content -Encoding Ascii $kh "$Hote ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEa+UjCM+SCZmbK/t5uUPcbtBymYv95cq+upONupR+64" }
        $sshArgs = "-N -L $($s.Port):$($s.Cible) -i ~/.ssh/id_ed25519_rao -o UserKnownHostsFile=~/.ssh/known_hosts_rao -o StrictHostKeyChecking=yes -o IdentitiesOnly=yes -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 camarade@$Hote"
    }
    $s.Proc = Start-Process ssh -WorkingDirectory $Root -WindowStyle Hidden -PassThru -ArgumentList $sshArgs
    $s.Depuis = Get-Date
    $s.Txt.Text = "Ouverture de $($s.Nom)…"
}

# ------------------------------------------------------------------ boutons des étapes
$Etapes = @(
    @(1, 'Tunnels chiffrés', 'Le datacenter compte ses tunnels IPsec.'),
    @(2, 'Routage et secours', 'Chaque site, joint par deux opérateurs.'),
    @(3, 'Échange autorisé', 'Le partenaire atteint son application.'),
    @(4, 'Échange interdit', 'Le partenaire vise la base de données.'),
    @(5, 'Journal du pare-feu', 'Les deux essais y sont tracés.'),
    @(6, 'Panne d''opérateur', 'Ligne A de l''agence coupée 10 s.'),
    @(7, 'Recette complète', '17 tests automatiques, avec preuves.')
)
foreach ($e in $Etapes) {
    $x = @"
<Button xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" Style="{DynamicResource Step}">
  <Grid>
    <Grid.ColumnDefinitions><ColumnDefinition Width="44"/><ColumnDefinition Width="*"/></Grid.ColumnDefinitions>
    <Border Width="30" Height="30" CornerRadius="15" BorderBrush="#101B2C" BorderThickness="1.5" VerticalAlignment="Top" HorizontalAlignment="Left" Margin="0,1,0,0">
      <TextBlock Text="$($e[0])" HorizontalAlignment="Center" VerticalAlignment="Center" FontWeight="SemiBold" FontSize="14"/>
    </Border>
    <StackPanel Grid.Column="1">
      <TextBlock Text="$([Security.SecurityElement]::Escape($e[1]))" FontSize="16" FontWeight="SemiBold"/>
      <TextBlock Text="$([Security.SecurityElement]::Escape($e[2]))" FontSize="13.5" Foreground="#5A6372" TextWrapping="Wrap" Margin="0,2,0,0"/>
    </StackPanel>
  </Grid>
</Button>
"@
    $btn = [Windows.Markup.XamlReader]::Parse($x)
    $btn.Tag = $e[0]
    $btn.Add_Click({ param($s, $ev) Invoke-Step ([int]$s.Tag) })
    [void]$Steps.Children.Add($btn)
    $StepButtons[[int]$e[0]] = $btn
}

# ------------------------------------------------------------------ état initial et événements
$TxtMode.Text = switch ($Mode) {
    'admin'    { 'Clé d''administration détectée : toutes les étapes, Proxmox et EVE-NG sont disponibles. Un clic sur une machine du schéma, ou sur la pastille du serveur, ouvre une console SSH.' }
    'camarade' { 'Clé de camarade détectée : vous pouvez ouvrir EVE-NG et Proxmox avec vos comptes personnels. Les tests automatiques se lancent depuis le PC qui a la clé d''administration ; dans EVE-NG, les consoles des nœuds permettent de refaire la démonstration à la main (docs/DEMO_EVE.md).' }
    default    { 'Aucune clé SSH trouvée. Lancez d''abord automation\connexion_rao.ps1 pour créer la vôtre.' }
}
if ($Mode -ne 'admin') { $ModeBox.Background = $B.OrangeBg }
$BtnEve.ToolTip = "Interface web d'EVE-NG : https://localhost:$PortEve (ssh -L ${PortEve}:10.99.0.10:443 lab-host)"
$BtnPve.ToolTip = 'Interface web du serveur Proxmox : https://localhost:8006 (ssh -L 8006:127.0.0.1:8006 lab-host)'
$BtnServer.ToolTip = 'Ouvrir une console SSH sur le serveur Proxmox (compte administrateur)'
if ($Mode -ne 'admin') { $BtnServer.IsEnabled = $false; $BtnServer.ToolTip = 'Console du serveur : réservée à la clé d''administration' }
if ($Mode -eq 'aucun') { $BtnEve.IsEnabled = $false; $BtnPve.IsEnabled = $false }
Set-BusyState $false
Set-Verdict 'Prêt pour la démonstration' 'Commencez par « Vérifier la maquette », puis suivez le scénario dans l''ordre.'

$BtnCheck.Add_Click({ if (-not $script:Job) { Set-Active 0; Start-Check } })
$BtnEve.Add_Click({ Open-Service 'eve' })
$BtnPve.Add_Click({ Open-Service 'pve' })
$BtnServer.Add_Click({ Open-Console 'lab-host' })
$BtnRepair.Add_Click({ Start-Repair })
$BtnClear.Add_Click({ $Term.Document.Blocks.Clear() })
$BtnCopy.Add_Click({
    $t = (New-Object Windows.Documents.TextRange($Term.Document.ContentStart, $Term.Document.ContentEnd)).Text
    if ($t.Trim()) { [Windows.Clipboard]::SetText($t) }
})
$win.Add_PreviewKeyDown({
    param($s, $e)
    $k = $e.Key.ToString()
    if ($k -match '^(D|NumPad)([1-7])$') { Invoke-Step ([int]$Matches[2]); $e.Handled = $true }
    elseif ($k -eq 'F5' -and $Mode -eq 'admin' -and -not $script:Job) { Set-Active 0; Start-Check; $e.Handled = $true }
})
$win.Add_Closing({
    foreach ($s in $Services.Values) {
        if ($s.Proc -and -not $s.Proc.HasExited) { Stop-Process -Id $s.Proc.Id -ErrorAction SilentlyContinue }
    }
    if ($script:Job) { $script:Job.PS.Stop() }
})

$script:Ticks = 0
$script:PhaseVue = ''
$timer = New-Object Windows.Threading.DispatcherTimer
$timer.Interval = [TimeSpan]::FromMilliseconds(120)
$timer.Add_Tick({
    $item = $null
    while ($sync.Queue.TryDequeue([ref]$item)) { Add-Line $item[0] $item[1] }
    if ($sync.Phase -ne $script:PhaseVue) { $script:PhaseVue = $sync.Phase; Show-Phase $sync.Phase }

    if ($script:Job -and $script:Job.Handle.IsCompleted) {
        $j = $script:Job; $script:Job = $null
        $res = $null; $err = ''
        try { $out = $j.PS.EndInvoke($j.Handle); if ($out.Count) { $res = $out[$out.Count - 1] } } catch { $err = $_.Exception.Message }
        $j.PS.Runspace.Dispose(); $j.PS.Dispose()
        Set-BusyState $false
        if ($res -is [hashtable]) { & $j.Fin $res }
        else { Set-Verdict 'La commande n''a pas abouti' "$err" 'ko' 'À vérifier' }
    }

    foreach ($s in $Services.Values) {
        if (-not $s.Depuis) { continue }
        if (Test-PortOuvert $s.Port) {
            $s.Depuis = $null
            Start-Process "https://localhost:$($s.Port)"
            Set-Verdict "$($s.Nom) est ouvert dans le navigateur" "Adresse https://localhost:$($s.Port), $($s.Aide). Le certificat est auto-signé : acceptez l'avertissement." 'ok'
            Update-Services
        } elseif ($s.Proc.HasExited -or ((Get-Date) - $s.Depuis).TotalSeconds -gt 15) {
            $s.Depuis = $null
            if (-not $s.Proc.HasExited) { Stop-Process -Id $s.Proc.Id -ErrorAction SilentlyContinue }
            $aide = "Le serveur refuse la connexion SSH, ou le port $($s.Port) est déjà pris par un autre programme."
            if ($Mode -eq 'camarade') { $aide = 'Votre clé n''est peut-être pas encore autorisée : lancez automation\connexion_rao.ps1 pour la copier et l''envoyer au responsable du serveur.' }
            Set-Verdict "$($s.Nom) n'a pas pu s'ouvrir" $aide 'ko' 'À vérifier'
            Update-Services
        }
    }
    if ((++$script:Ticks % 16) -eq 0 -or $script:Ticks -eq 1) { Update-Services }
})
$timer.Start()
[void]$win.ShowDialog()
