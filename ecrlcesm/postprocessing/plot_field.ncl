load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"

;==========================================================    

print("infile: " + infile)
print("field: " + field)
print("level: " + level)

plev=(/level/)

function get_field(infile,field)

local tmp, tmp_new
begin

  
  f  = addfile (infile, "r")
  
  u   = f->U ; (time,lev,lat,lon) 
  v   = f->V                     
  t   = f->T ; K
  ps  = f->PS ; Pa
  z   = f->Z3 ; m
  ke  = f->UU+f->VV
  
  hyam = f->hyam
  hybm = f->hybm
  p0   = f->P0 ; p0=100000
  p0mb = p0/100
  ps@long_name = "surface pressure"
  
  ke@long_name = "kinetic energy"
  ke@units = f->UU@units
  copy_VarCoords(f->UU,ke)
 
  if ((field.eq."P").or.(field.eq."PV")) then
    p = pres_hybrid_ccm (ps,p0,hyam,hybm) 
    copy_VarCoords(t, p)
    p@units = ps@units
    p@long_name = "hybrid pressure levels"
  end if

  delete(f)

  if (field.eq."PV") then
    PV  = pot_vort_hybrid(p,u,v,t,t&lat, gridType, 0 )
    printVarSummary(PV)
    printMinMax(PV,0)
  end if
  
  if (field.eq."PV") then
    tmp=PV
    delete(PV)
  else if (field.eq."Z3") then
    tmp=z
    delete(z)
  else if (field.eq."U") then
    tmp=u
    delete(u)
  else if (field.eq."V") then
    tmp=v
    delete(v)
  else if (field.eq."T") then
    tmp=t
    delete(t)
  else if (field.eq."PS") then
    tmp=ps
    delete(ps)
  else if (field.eq."P") then
    tmp=p
    delete(p)
  else if (field.eq."KE") then
    tmp=ke
    delete(ke)

  end if
  end if  
  end if  
  end if
  end if
  end if
  end if
  end if
  
  rank=dimsizes(dimsizes(tmp))
  
  interp = 2
  extrap = False

  if (rank.eq.4) then
    tmp_new = vinth2p(tmp,hyam,hybm,plev,ps,interp,p0mb,1,extrap)
    delete(tmp)
    tmp = tmp_new(:,{plev(0)},:,:)
    delete(tmp_new)
  end if
  return(tmp)
end

;************************************************
; create plots
;************************************************

tmp = get_field(infile,field)

dims = dimsizes(tmp)
rank = dimsizes(dims)

array = dim_avg_n_Wrap(tmp,0)

outname=outdir+field+"_avg_"+level+"_"+case_name

res                      = True
res@gsnMaximize          = True
res@cnFillOn             = True ; turn on color
res@cnLinesOn            = False
res@cnLineLabelsOn       = False
res@cnLevelSelectionMode = "AutomaticLevels"
res@gsnPaperOrientation  = "portrait"
res@cnConstFEnableFill = True
res@cnConstFLabelOn = False
res@mpOutlineOn = False
res@mpFillOn = False
res@gsnDraw      = False
res@gsnFrame     = False
res@gsnLeftString = ""
res@gsnRightString = ""
res@gsnPolar = "NH"

minVal = min(array)
maxVal = max(array)
diff = maxVal-minVal
meanVal = avg(array)
minVal = meanVal - diff/4.0
maxVal = meanVal + diff/4.0

res@cnMinLevelValF = minVal
res@cnMaxLevelValF = maxVal
res@cnLevelSpacingF = (maxVal-minVal)/16
res@cnLevelSpacingF = 0.5*res@cnLevelSpacingF

if (rank.eq.3) then
  res@gsnCenterString = plev(0) + " hPa"
end if

res@tiMainString = field+" AVG "   
wks = gsn_open_wks("png",outname) 
plot1 = gsn_csm_contour_map_polar(wks,array(:,:),res) 
  
draw(plot1)

frame(wks)

print("Saved file: " + outname + ".png")

