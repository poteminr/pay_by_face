Задача финального этапа профиля ФинТех ОНТИ 2018/19
====

## Ввведение

Этот репозиторий предназначен для публикации решения задачи финального этапа профиля "Программная инженерия финансовых технологий" Олимпиады НТИ 2018/19.

Формулировка задачи приведена [здесь](task-description.md).

## Подготовка

Прежде чем решать задачу, создайте ветку (_branch_) `develop` в этом репозитории. После этого вы можете склонировать репозиторий к себе на локальную машину и готовить код, решающий задачу.

Вы можете создать сколько угодно других веток, если это необходимо для одновременной командной работы в рамках проекта. 

### Проверка решения

Каждый раз, когда вы будете делать `push` в ветку `develop` вашего репозитория у вас будет автоматически проводиться предварительная проверка решения. Результат проверки можно будет видеть в GitLab в разделе `CI/CI -> Pipelines`. Проверка решения занимает довольно много - имейте это в виду, что подход _try&fix_ попросту будет отнимать у вас время. 

Если проверка прошла успешно, то вы увидете в самом верху списка зеленый значок с надписью `passed`.

Если проверка не прошла, то значок будет красный и надпись будет гласить `failed`. Щелкните по значку (а на новом экране на надпись `test` рядом с красным крестиком), чтобы увидеть на какой именно комманде проверка не прошла. Вам будет показан лог запуска вашего скрипта с различными параметрами.

Проверка вашего решения требует следующих конфигурационных данных:
  * Ключ подписки на _Microsoft Face API_ для подготовки конфигурационных файлов перед запуском вашего решения.
  * Приватный ключ аккаунта 0x1bb86232B0EA8A331C13D561fF7831f9720a01F7, который будет содержать не меньше 2 тестовых POA. Пополните аккаунт на 2 монеты в [_faucet_ в сети Sokol](https://faucet-sokol.herokuapp.com/) сразу после создания ветки `develop`. Следите за тем, чтобы баланс на этом аккаунте не опускался ниже 2 тестовых POA.  

Эти ключи должны быть добавлены в переменные CI/CD. Это может сделать только владелец репозитория. Обратитесь к нему за помощью.

Чтобы ваше решение могло проходить автоматическую проверку в GitLab не удаляйте и не изменяйте файл `.gitlab-ci.yml`.

### Отправка решения на приемку

Как только вы считате, что ваше решение готово (в той или иной степени), то нужно создать Merge Request для слияния изменений из ветки `develop` в ветку `master`. При создании Merge Request в качестве ответственного (assignee) укажите того, кто будет отвечать за приемку результатов.