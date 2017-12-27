wrapText = (context, text, x, y, maxWidth, lineHeight) ->
  words = text.split(' ')
  line = ''
  n = 0
  while n < words.length
    testLine = line + words[n] + ' '
    metrics = context.measureText(testLine)
    testWidth = metrics.width
    if testWidth > maxWidth and n > 0
      context.fillText line, x, y
      line = words[n] + ' '
      y += lineHeight
    else
      line = testLine
    n++
  context.fillText line, x, y

fetchImage = ->
  if $('body').hasClass('new')
    fetchNewImage()
  else
     fetchExistingImage()

fetchNewImage = ->
  oldUrl = $('img#preview').attr('src')
  newUrl = '/admin/twitter_image_preview?' + $('form').serialize()
  if oldUrl != newUrl
    chart = new Image()
    chart.onload = ->
      canvas = document.getElementById('preview')
      ctx = canvas.getContext('2d')
      background = document.getElementById('background')
      ctx.drawImage(background, 0, 0)
      ctx.drawImage(chart, 0, 110)
      ctx.font = 'bold 56px PT Sans'
      ctx.fillStyle = '#EEEEEE'
      ctx.textAlign = 'center'
      symbol = $('#admin_twitter_image_symbol').val()
      timeframe = $('#admin_twitter_image_timeframe').val()
      ctx.fillText("#{window.symbol} #{window.timeframe}", 820, 80)
      ctx.font = 'bold 32px PT Sans'
      ctx.fillStyle = '#363631'
      ctx.textAlign = 'center'
      date = $.format.date($.now(), 'yyyy-MM-dd HH:mm UTC')
      ctx.fillText(date, 1810, 200)
      ctx.font = '17px PT Sans'
      ctx.fillText('Provided information is not an investing advice', 1810, 1007)
      ctx.textAlign = 'left'
      offset = 220
    chart.src = newUrl

fetchExistingImage = ->
  oldUrl = $('img#preview').attr('src')
  patterns = []
  for pattern in $('table#patterns input[type=checkbox]:checked').parents('tr')
    values = []
    $(pattern).children('td:gt(0)').each ->
      values.push(@innerText)
    patterns.push(values)
  levels = []
  for level in $('table#levels input[type=checkbox]:checked').parents('tr')
    values = []
    $(level).children('td:gt(0)').each ->
      values.push(@innerText)
    levels.push(values)
  newUrl = '/admin/twitter_image_preview/' + window.image_id + '?' + $('form').serialize()
  if oldUrl != newUrl
    chart = new Image()
    chart.onload = ->
      canvas = document.getElementById('preview')
      ctx = canvas.getContext('2d')
      background = document.getElementById('background')
      ctx.drawImage(background, 0, 0)
      ctx.drawImage(chart, 0, 110)
      ctx.font = 'bold 56px PT Sans'
      ctx.fillStyle = '#EEEEEE'
      ctx.textAlign = 'center'
      symbol = $('#admin_twitter_image_symbol').val()
      timeframe = $('#admin_twitter_image_timeframe').val()
      ctx.fillText("#{window.symbol} #{window.timeframe}", 820, 80)
      ctx.font = 'bold 32px PT Sans'
      ctx.fillStyle = '#363631'
      ctx.textAlign = 'center'
      date = $.format.date($.now(), 'yyyy-MM-dd HH:mm UTC')
      ctx.fillText(date, 1810, 200)
      ctx.font = '17px PT Sans'
      ctx.fillText('Provided information is not an investing advice', 1810, 1007)
      ctx.textAlign = 'left'
      offset = 220
      if patterns.length > 0
        offset += 40
        ctx.font = 'bold 22px PT Sans'
        ctx.fillText('Patterns', 1610, offset)
        offset += 40
        ctx.font = '22px PT Sans'
        for pattern in patterns
          ctx.fillText(pattern[0], 1610, offset)
          ctx.fillText(pattern[2], 1760, offset)
          ctx.fillText(pattern[1], 1970, offset)
          offset += 40
      if levels.length > 0
        offset += 40
        ctx.font = 'bold 22px PT Sans'
        ctx.fillText('Levels', 1610, offset)
        offset += 40
        ctx.font = '22px PT Sans'
        for level in levels
          ctx.fillText(level[0], 1610, offset)
          ctx.fillText(level[1], 1760, offset)
          offset += 40
      if $('#admin_twitter_image_comment').val()
        offset += 40
        ctx.font = 'bold 22px PT Sans'
        ctx.fillText('Comment', 1610, offset)
        offset += 40
        ctx.font = '22px PT Sans'
        wrapText(ctx, $('#admin_twitter_image_comment').val(), 1610, offset, 410, 36)
    chart.src = newUrl

countdown = ->
  @time += 1
  $('#reloader').progress('increment')
  if @time == 10
    fetchImage()
  else
    @timeout = setTimeout(countdown, 200)

tryFetchImage = ->
  clearTimeout(@timeout)
  $('#reloader').progress('reset')
  @time = 0
  @timeout = setTimeout(countdown, 200)

$(document).on 'turbolinks:load', ->
  return unless $('body').hasClass('twitter_images')
  $('.ui.dropdown').dropdown()
  $('.ui.checkbox').checkbox()
  $('#reloader').progress
    total: 10
    value: 10
  $('img#preview').error ->
    $('img#preview').attr('src', '')
  $('form :input').on 'change input', ->
    tryFetchImage()
  fetchImage()
  canvas = document.getElementById('preview')
  ctx = canvas.getContext('2d')
  background = document.getElementById('background')
  ctx.drawImage(background, 0, 0)
  downloadLink = $('#save-image')
  downloadLink.on 'click', (e) ->
    downloadLink.attr('href', canvas.toDataURL())
    date = $.format.date($.now(), 'yyyy-MM-dd HH:mm')
    downloadLink.attr('download', "Twitter #{window.symbol} #{date}.png")
