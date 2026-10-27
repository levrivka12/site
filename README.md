# האתר של רבקה לב — פיזיותרפיה התפתחותית ושיקום רצפת אגן

אתר סטטי עברי (RTL) עבור `www.rivkalev.com`, המנוהל ב-GitHub Pages (ראו `CNAME`).
הבסיס: התבנית [Modern Business](https://startbootstrap.com/template-overviews/modern-business/)
של [Start Bootstrap](https://startbootstrap.com/), שהותאמה לרבקה לב (מבוססת Bootstrap 4.5.0).

## עמודים

| עמוד                                | תיאור                                                                 |
| ----------------------------------- | --------------------------------------------------------------------- |
| `index.html`                        | עמוד הבית: היכרות, שטחי טיפול אישי, כרזת תמונות וטופס פנייה             |
| `pediatric_physical_therapy.html`   | פיזיותרפיה התפתחותית לתינוקות וילדים                                    |
| `pelvic_floor_rehabilitation.html`  | שיקום רצפת אגן לנשים                                                   |
| `pediatric_pelvic_floor.html`       | רצפת אגן לילדים, גמילה מחיתולים ומידע על ICCS                           |
| `lectures.html`, `sadnaot.html`     | הרצאות וסדנאות                                                         |
| `movies.html`, `posts.html`, `tips.html`, `reviews.html` | סרטוני הדרכה, פוסטים, טיפים והמלצות |
| `contact.html`                      | פרטי קשר, מפה click-to-load וטופס פנייה                                 |
| `privacy-policy.html`               | מדיניות פרטיות ועוגיות                                                 |
| `terms-of-use.html`                 | תנאי שימוש באתר                                                        |
| `accessibility-statement.html`      | הצהרת נגישות (ת"י 5568 / WCAG 2.1 AA)                                   |
| `404.html`                          | עמוד שגיאה עברי ל-GitHub Pages                                          |

## פרטיות ועוגיות

- Google Analytics (`UA-179818286-1`) מופעל עם `anonymize_ip: true`.
- בכל עמוד מופיעה הודעת עוגיות עם הסבר וקישור למדיניות הפרטיות ולאפשרות הפסקת המעקב.
- סרטונים מוטמעים מ`youtube.com` (התחום הרגיל — נדרש כדי שהתצוגה המקדימה של YouTube תעבוד ללא שגיאה 153), ומפת Google נטענת רק בלחיצה על הכפתור.
- טפסי הקשר שולחים את הפרטים באמצעות Google Apps Script אל תיבת המייל של רבקה לב,
  אחרי אישור המסירה בטופס ולפי מדיניות הפרטיות.

## הרצת בדיקות

הבדיקות בנויות ב-Python עם `unittest` (אין צורך ב-node). דרושים `requests` ו`lxml`:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

## פריסה

העברת הקובצים אל ענף `gh-pages` מפרסמת את האתר ב-https://www.rivkalev.com (GitHub Pages).
