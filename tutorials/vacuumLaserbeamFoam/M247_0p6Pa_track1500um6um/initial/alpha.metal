FoamFile
{
    version 2.0;
    format ascii;
    class volScalarField;
    location "0";
    object alpha.metal;
}
dimensions [0 0 0 0 0 0 0];
internalField uniform 0;

boundaryField
{
    bottomWall { type zeroGradient; }
    sideWalls { type zeroGradient; }
    atmosphere
    {
        type inletOutlet;
        inletValue uniform 0;
        value uniform 0;
    }
}
